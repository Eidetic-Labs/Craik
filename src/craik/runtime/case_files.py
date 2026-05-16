"""Case file assembly from local project and task state."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from craik.contracts.models import (
    Assumption,
    CaseFile,
    EvidenceReference,
    ProjectProfile,
    TaskRequest,
)
from craik.runtime.intent_locks import IntentLockManager
from craik.runtime.policy import generate_policy_envelope
from craik.runtime.redaction import redact
from craik.runtime.store import LocalStore


class CaseFileError(RuntimeError):
    """Base error for case file assembly failures."""


class TaskNotFoundError(CaseFileError):
    """Raised when a task cannot be found."""


class ProjectNotFoundError(CaseFileError):
    """Raised when a task references an unknown project."""


@dataclass(frozen=True)
class CaseFileAssembler:
    """Build deterministic case files from local project and task contracts."""

    store: LocalStore

    def build(self, task_id: str, *, max_tokens: int = 24000) -> CaseFile:
        """Build and persist a case file for a task."""
        task = self.store.get_task(task_id)
        if task is None:
            raise TaskNotFoundError(f"unknown task: {task_id}")
        project = self.store.get_project(task.project_id)
        if project is None:
            raise ProjectNotFoundError(f"unknown project for task {task_id}: {task.project_id}")

        repo_root = Path(project.repo.local_path)
        docs, adrs, omitted_docs = _discover_docs(project, repo_root, max_tokens=max_tokens)
        repo_state = _repo_state(project, repo_root)
        evidence = _evidence(task, project, docs, adrs, repo_state)
        assumptions = _assumptions(task, project, docs, omitted_docs)
        stale_risks = _stale_risks(repo_state, docs, assumptions)
        policy = generate_policy_envelope(task_id=task.id, actor="agent:case-file")
        intent_lock = IntentLockManager(self.store).ensure_for_task(task)
        case_file = CaseFile(
            id=f"case_{task.id.removeprefix('task_')}",
            task_id=task.id,
            objective=task.objective,
            policy_envelope_id=policy.id,
            intent_lock_id=intent_lock.id,
            facts=[],
            evidence=evidence,
            assumptions=assumptions,
            docs=docs,
            adrs=adrs,
            repo_state=repo_state,
            github_state={"status": "not_loaded"},
            recent_handoffs=[],
            stale_risks=stale_risks,
            contradictions=[],
            verification_plan=_verification_plan(task),
            context_budget=_context_budget(
                max_tokens=max_tokens,
                docs=docs,
                adrs=adrs,
                omitted_docs=omitted_docs,
                evidence=evidence,
                assumptions=assumptions,
            ),
        )
        self.store.put_case_file(case_file)
        return case_file

    def get(self, case_file_id: str) -> CaseFile | None:
        """Load one persisted case file."""
        return self.store.get_case_file(case_file_id)

    def latest_for_task(self, task_id: str) -> CaseFile | None:
        """Return the stable case file for a task when present."""
        return self.store.get_case_file(f"case_{task_id.removeprefix('task_')}")


def _discover_docs(
    project: ProjectProfile,
    repo_root: Path,
    *,
    max_tokens: int,
) -> tuple[list[str], list[str], list[str]]:
    docs: list[str] = []
    adrs: list[str] = []
    omitted: list[str] = []
    budget_chars = max_tokens * 4
    used_chars = 0
    immutable_prefixes = tuple(_normalize_path(path) for path in project.docs.immutable_paths)

    for configured in sorted(project.docs.paths):
        path = repo_root / configured
        candidates = _doc_candidates(repo_root, path)
        for candidate in candidates:
            relative = _relative(repo_root, candidate)
            size = candidate.stat().st_size
            if used_chars + size > budget_chars:
                omitted.append(relative)
                continue
            used_chars += size
            if _is_immutable(relative, immutable_prefixes):
                adrs.append(relative)
            else:
                docs.append(relative)

    return sorted(set(docs)), sorted(set(adrs)), sorted(set(omitted))


def _doc_candidates(repo_root: Path, path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        return []
    return sorted(
        candidate
        for candidate in path.rglob("*")
        if candidate.is_file() and candidate.suffix.lower() in {".md", ".mdx", ".txt"}
    )


def _repo_state(project: ProjectProfile, repo_root: Path) -> dict[str, Any]:
    status = _git(repo_root, "status", "--short")
    branch = _git(repo_root, "branch", "--show-current")
    rev = _git(repo_root, "rev-parse", "--short", "HEAD")
    return {
        "branch": redact(branch.stdout.strip() or "detached").value,
        "default_branch": project.repo.default_branch,
        "dirty": bool(status.stdout.strip()),
        "head": redact(rev.stdout.strip() or "unknown").value,
        "immutable_paths": list(project.docs.immutable_paths),
        "repo": redact(project.repo.remote or project.repo.local_path).value,
        "status": "clean" if not status.stdout.strip() else "dirty",
    }


def _evidence(
    task: TaskRequest,
    project: ProjectProfile,
    docs: list[str],
    adrs: list[str],
    repo_state: dict[str, Any],
) -> list[EvidenceReference]:
    evidence = [
        EvidenceReference(
            id=f"evidence_{task.id}_task",
            source="local_store",
            kind="other",
            locator=task.id,
            summary="Task request loaded from local store.",
        ),
        EvidenceReference(
            id=f"evidence_{task.id}_project",
            source="local_store",
            kind="other",
            locator=project.id,
            summary="Project profile loaded from local store.",
        ),
        EvidenceReference(
            id=f"evidence_{task.id}_repo_status",
            source="git",
            kind="command",
            locator="git status --short",
            summary=f"Repository status is {repo_state['status']}.",
            metadata={"branch": repo_state["branch"], "dirty": repo_state["dirty"]},
        ),
    ]
    for path in docs:
        evidence.append(_file_evidence(task.id, path, immutable=False))
    for path in adrs:
        evidence.append(_file_evidence(task.id, path, immutable=True))
    return evidence


def _file_evidence(task_id: str, path: str, *, immutable: bool) -> EvidenceReference:
    return EvidenceReference(
        id=f"evidence_{task_id}_{_slug(path)}",
        source=path,
        kind="file",
        locator=path,
        summary="Immutable documentation source." if immutable else "Documentation source.",
        metadata={"immutable": immutable},
    )


def _assumptions(
    task: TaskRequest,
    project: ProjectProfile,
    docs: list[str],
    omitted_docs: list[str],
) -> list[Assumption]:
    assumptions = [
        Assumption(
            id=f"assumption_{task.id}_memory_not_loaded",
            task_id=task.id,
            statement="No memory facts were loaded into this case file.",
            rationale=(
                f"The configured memory backend is {project.memory.backend}, but memory loading is "
                "not implemented in the local case assembler yet."
            ),
            confidence=1.0,
            status="open",
        ),
        Assumption(
            id=f"assumption_{task.id}_github_not_loaded",
            task_id=task.id,
            statement="No GitHub issue or pull request state was loaded into this case file.",
            rationale="The GitHub read adapter is not implemented yet.",
            confidence=1.0,
            status="open",
        ),
    ]
    if not docs:
        assumptions.append(
            Assumption(
                id=f"assumption_{task.id}_docs_missing",
                task_id=task.id,
                statement="No mutable documentation files were discovered for this project.",
                rationale=(
                    "Configured documentation paths were missing or only contained immutable docs."
                ),
                confidence=0.9,
                status="open",
            )
        )
    if omitted_docs:
        assumptions.append(
            Assumption(
                id=f"assumption_{task.id}_context_omitted",
                task_id=task.id,
                statement="Some documentation was omitted from the case file context budget.",
                rationale="Configured docs exceeded the requested context budget.",
                confidence=1.0,
                status="open",
            )
        )
    return assumptions


def _stale_risks(
    repo_state: dict[str, Any],
    docs: list[str],
    assumptions: list[Assumption],
) -> list[str]:
    risks: list[str] = []
    if docs:
        risks.append("Documentation may be stale relative to implementation and memory state.")
    if repo_state["dirty"]:
        risks.append("Repository has uncommitted changes that may affect case file accuracy.")
    if assumptions:
        risks.append("Case file contains open assumptions that require downstream review.")
    return risks


def _verification_plan(task: TaskRequest) -> list[str]:
    plan = ["Review case file assumptions before acting.", "Run repository-appropriate tests."]
    if task.mode in {"review", "verify"}:
        plan.insert(0, "Compare findings against cited evidence.")
    return plan


def _context_budget(
    *,
    max_tokens: int,
    docs: list[str],
    adrs: list[str],
    omitted_docs: list[str],
    evidence: list[EvidenceReference],
    assumptions: list[Assumption],
) -> dict[str, Any]:
    return {
        "max_tokens": max_tokens,
        "estimated_tokens": _estimate_tokens(docs + adrs),
        "docs_included": len(docs),
        "adrs_included": len(adrs),
        "docs_omitted": omitted_docs,
        "evidence_count": len(evidence),
        "assumption_count": len(assumptions),
    }


def _estimate_tokens(paths: list[str]) -> int:
    return sum(max(1, len(path) // 4) for path in paths)


def _is_immutable(path: str, immutable_prefixes: tuple[str, ...]) -> bool:
    normalized = _normalize_path(path)
    return any(
        normalized == prefix.rstrip("/") or normalized.startswith(f"{prefix.rstrip('/')}/")
        for prefix in immutable_prefixes
    )


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _slug(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", "-C", str(cwd), *args),
        check=False,
        text=True,
        capture_output=True,
    )
