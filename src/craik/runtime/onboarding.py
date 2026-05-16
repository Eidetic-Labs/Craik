"""Agent-native onboarding assembly."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from craik.contracts.models import (
    AgentOnboarding,
    ContradictionReport,
    Handoff,
    PolicyProfile,
    ProjectProfile,
    TaskRequest,
)
from craik.runtime.instruction_sources import instruction_stale_risk_warnings
from craik.runtime.policy import generate_policy_envelope
from craik.runtime.project_registry import ProjectRegistry
from craik.runtime.redaction import redact
from craik.runtime.store import LocalStore


class OnboardingError(RuntimeError):
    """Base error for onboarding failures."""


class OnboardingProjectNotFoundError(OnboardingError):
    """Raised when a project cannot be found for onboarding."""


@dataclass(frozen=True)
class AgentOnboardingBuilder:
    """Build runner-readable project onboarding from local Craik state."""

    store: LocalStore

    def build(
        self,
        project_id_or_name: str,
        *,
        policy_profile: PolicyProfile = "strict",
        trusted_local_fail_open: bool = False,
        max_recent_handoffs: int = 5,
    ) -> AgentOnboarding:
        """Build a deterministic onboarding report for a registered project."""
        project = ProjectRegistry(self.store).get_project(project_id_or_name)
        if project is None:
            raise OnboardingProjectNotFoundError(f"unknown project: {project_id_or_name}")

        tasks = _project_tasks(project, self.store.list_tasks())
        handoffs = _recent_handoffs(project, self.store.list_handoffs(), max_recent_handoffs)
        contradictions = _project_contradictions(
            task_ids={task.id for task in tasks},
            reports=self.store.list_contradictions(),
        )
        case_risks = _case_file_risks(tasks, self.store.list_case_files())
        repo_state = _repo_state(project)
        docs_boundaries = _docs_boundaries(project)
        active_policy = generate_policy_envelope(
            task_id=f"onboard_{project.id}",
            actor="agent:onboarding",
            profile=policy_profile,
            trusted_local_fail_open=trusted_local_fail_open,
        )
        stale_warnings = _stale_warnings(
            project=project,
            tasks=tasks,
            handoffs=handoffs,
            contradictions=contradictions,
            repo_state=repo_state,
            docs_boundaries=docs_boundaries,
            case_risks=case_risks,
            instruction_risks=instruction_stale_risk_warnings(self.store, project.id),
        )

        payload = AgentOnboarding(
            id=f"onboarding_{project.id.removeprefix('project_')}",
            project_id=project.id,
            project_model=_project_model(project, tasks, repo_state),
            active_policy=active_policy,
            docs_boundaries=docs_boundaries,
            recent_handoffs=[_handoff_summary(handoff) for handoff in handoffs],
            unresolved_contradictions=contradictions,
            stale_risk_warnings=stale_warnings,
            validation_commands=_validation_commands(Path(project.repo.local_path)),
            stigmem_backend_status=_stigmem_backend_status(project),
            known_traps=_known_traps(project),
            allowed_next_actions=_allowed_next_actions(tasks, contradictions),
            created_at=datetime.now(UTC),
        )
        return AgentOnboarding.model_validate(redact(payload.model_dump(by_alias=True)).value)


def _project_tasks(project: ProjectProfile, tasks: list[TaskRequest]) -> list[TaskRequest]:
    return sorted(
        (task for task in tasks if task.project_id == project.id),
        key=lambda task: (task.created_at, task.id),
    )


def _recent_handoffs(
    project: ProjectProfile,
    handoffs: list[Handoff],
    limit: int,
) -> list[Handoff]:
    matching = (handoff for handoff in handoffs if handoff.project_id == project.id)
    return sorted(matching, key=lambda handoff: (handoff.created_at, handoff.id), reverse=True)[
        : max(0, limit)
    ]


def _project_contradictions(
    *,
    task_ids: set[str],
    reports: list[ContradictionReport],
) -> list[ContradictionReport]:
    return sorted(
        (
            report
            for report in reports
            if report.status == "open" and (report.task_id is None or report.task_id in task_ids)
        ),
        key=lambda report: report.id,
    )


def _case_file_risks(tasks: list[TaskRequest], case_files: list[Any]) -> list[str]:
    project_task_ids = {task.id for task in tasks}
    risks: list[str] = []
    for case_file in case_files:
        if project_task_ids and case_file.task_id not in project_task_ids:
            continue
        for risk in case_file.stale_risks:
            risks.append(f"{case_file.task_id}: {risk}")
    return sorted(set(risks))


def _project_model(
    project: ProjectProfile,
    tasks: list[TaskRequest],
    repo_state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": project.id,
        "name": project.name,
        "repo": repo_state,
        "docs": project.docs.model_dump(mode="json"),
        "memory": project.memory.model_dump(mode="json"),
        "policies": list(project.policies),
        "task_count": len(tasks),
        "open_task_ids": [task.id for task in tasks],
    }


def _docs_boundaries(project: ProjectProfile) -> dict[str, Any]:
    repo_root = Path(project.repo.local_path)
    mutable_paths = list(project.docs.paths)
    immutable_paths = list(project.docs.immutable_paths)
    return {
        "mutable_paths": mutable_paths,
        "immutable_paths": immutable_paths,
        "missing_mutable_paths": [
            path for path in mutable_paths if not (repo_root / path).exists()
        ],
        "missing_immutable_paths": [
            path for path in immutable_paths if not (repo_root / path).exists()
        ],
        "adr_policy": (
            "Treat immutable paths as read-only evidence unless explicit approval exists."
        ),
    }


def _repo_state(project: ProjectProfile) -> dict[str, Any]:
    repo_root = Path(project.repo.local_path)
    status = _git(repo_root, "status", "--short")
    branch = _git(repo_root, "branch", "--show-current")
    head = _git(repo_root, "rev-parse", "--short", "HEAD")
    return {
        "local_path": str(redact(str(repo_root)).value),
        "remote": redact(project.repo.remote).value if project.repo.remote else None,
        "default_branch": project.repo.default_branch,
        "branch": redact(branch.stdout.strip() or "detached").value,
        "head": redact(head.stdout.strip() or "unknown").value,
        "dirty": bool(status.stdout.strip()),
        "status": "clean" if not status.stdout.strip() else "dirty",
    }


def _stale_warnings(
    *,
    project: ProjectProfile,
    tasks: list[TaskRequest],
    handoffs: list[Handoff],
    contradictions: list[ContradictionReport],
    repo_state: dict[str, Any],
    docs_boundaries: dict[str, Any],
    case_risks: list[str],
    instruction_risks: list[str],
) -> list[str]:
    warnings: list[str] = []
    if repo_state["dirty"]:
        warnings.append("Repository has uncommitted changes; verify state before acting.")
    if not tasks:
        warnings.append("No task requests are recorded for this project.")
    if not handoffs:
        warnings.append("No prior handoffs are recorded for this project.")
    if contradictions:
        warnings.append("Unresolved contradiction reports require review before promotion to fact.")
    if docs_boundaries["missing_mutable_paths"] or docs_boundaries["missing_immutable_paths"]:
        warnings.append("Configured documentation paths are missing from the repository.")
    if project.memory.backend == "stigmem" and not os.environ.get("CRAIK_STIGMEM_URL"):
        warnings.append("Project is configured for Stigmem but CRAIK_STIGMEM_URL is not set.")
    warnings.extend(case_risks)
    warnings.extend(instruction_risks)
    return sorted(set(warnings))


def _validation_commands(repo_root: Path) -> list[str]:
    if (repo_root / "pyproject.toml").exists():
        return [
            "uv run --python 3.12 --extra dev ruff check .",
            "uv run --python 3.12 --extra dev mypy",
            "uv run --python 3.12 --extra dev pytest",
        ]
    return ["Run the repository's documented validation commands."]


def _stigmem_backend_status(project: ProjectProfile) -> dict[str, Any]:
    return {
        "backend": project.memory.backend,
        "scope": project.memory.scope,
        "status": (
            "configured_not_checked" if project.memory.backend == "stigmem" else "not_configured"
        ),
        "node_url_configured": bool(os.environ.get("CRAIK_STIGMEM_URL")),
        "api_key_configured": bool(os.environ.get("CRAIK_STIGMEM_API_KEY")),
    }


def _known_traps(project: ProjectProfile) -> list[str]:
    traps = [
        "Do not edit immutable documentation paths without explicit approval.",
        "Do not treat assumptions or stale-risk warnings as facts.",
        "Do not print or persist secrets from environment variables or credentials.",
        "Create a handoff before ending non-trivial work.",
    ]
    if project.memory.backend == "stigmem":
        traps.append("Direct Stigmem writes require policy approval and evidence.")
    return traps


def _allowed_next_actions(
    tasks: list[TaskRequest],
    contradictions: list[ContradictionReport],
) -> list[str]:
    actions = [
        "Read this onboarding report and preserve its boundaries in the run plan.",
        "Inspect cited project docs and immutable paths as evidence.",
        "Run the listed validation commands after making changes.",
        "Record a structured handoff with residual risks and next steps.",
    ]
    if tasks:
        actions.append("Build or refresh a case file for the active task before implementation.")
    if contradictions:
        actions.append("Review unresolved contradictions before changing related docs or facts.")
    return actions


def _handoff_summary(handoff: Handoff) -> dict[str, Any]:
    return {
        "id": handoff.id,
        "task_id": handoff.task_id,
        "status": handoff.status,
        "summary": handoff.summary,
        "next_steps": list(handoff.next_steps),
        "created_at": handoff.created_at.isoformat(),
    }


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", "-C", str(cwd), *args),
        check=False,
        text=True,
        capture_output=True,
    )
