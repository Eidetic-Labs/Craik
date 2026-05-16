"""Case file assembly from local project and task state."""

from __future__ import annotations

import fnmatch
import os
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
from craik.runtime.github import GitHubReadAdapter
from craik.runtime.instruction_sources import instruction_stale_risk_warnings
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


DEFAULT_DISCOVERY_EXCLUDE = (
    ".git/**",
    ".hg/**",
    ".svn/**",
    ".mypy_cache/**",
    ".pytest_cache/**",
    ".ruff_cache/**",
    ".tox/**",
    ".venv/**",
    "__pycache__/**",
    "build/**",
    "coverage/**",
    "dist/**",
    "generated/**",
    "archive/**",
    "docs/archive/**",
    "docs/build/**",
    "node_modules/**",
    "site/**",
    "vendor/**",
    "**/.git/**",
    "**/.mypy_cache/**",
    "**/.pytest_cache/**",
    "**/.ruff_cache/**",
    "**/__pycache__/**",
    "**/build/**",
    "**/coverage/**",
    "**/dist/**",
    "**/generated/**",
    "**/archive/**",
    "**/node_modules/**",
    "**/vendor/**",
)


@dataclass(frozen=True)
class DiscoveryOverrides:
    """One-off user overrides for repository context discovery."""

    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class DiscoveredDocs:
    """Documentation discovered for a case file."""

    docs: list[str]
    adrs: list[str]
    omitted: list[str]
    excluded: list[dict[str, str]]
    rules: dict[str, list[str]]


@dataclass(frozen=True)
class CaseFileAssembler:
    """Build deterministic case files from local project and task contracts."""

    store: LocalStore
    github_adapter: GitHubReadAdapter | None = None

    def build(
        self,
        task_id: str,
        *,
        max_tokens: int = 24000,
        discovery_overrides: DiscoveryOverrides | None = None,
    ) -> CaseFile:
        """Build and persist a case file for a task."""
        task = self.store.get_task(task_id)
        if task is None:
            raise TaskNotFoundError(f"unknown task: {task_id}")
        project = self.store.get_project(task.project_id)
        if project is None:
            raise ProjectNotFoundError(f"unknown project for task {task_id}: {task.project_id}")

        repo_root = Path(project.repo.local_path)
        discovered = _discover_docs(
            project,
            repo_root,
            max_tokens=max_tokens,
            overrides=discovery_overrides or DiscoveryOverrides(),
        )
        repo_state = _repo_state(project, repo_root)
        github_state = _github_state(self.github_adapter, project, repo_state)
        evidence = _evidence(task, project, discovered.docs, discovered.adrs, repo_state)
        assumptions = _assumptions(
            task,
            project,
            discovered.docs,
            discovered.omitted,
            github_state,
        )
        stale_risks = [
            *_stale_risks(repo_state, discovered.docs, assumptions),
            *instruction_stale_risk_warnings(self.store, project.id),
        ]
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
            docs=discovered.docs,
            adrs=discovered.adrs,
            repo_state=repo_state,
            github_state=github_state,
            recent_handoffs=[],
            stale_risks=stale_risks,
            contradictions=[],
            verification_plan=_verification_plan(task),
            context_budget=_context_budget(
                max_tokens=max_tokens,
                docs=discovered.docs,
                adrs=discovered.adrs,
                omitted_docs=discovered.omitted,
                excluded_docs=discovered.excluded,
                discovery_rules=discovered.rules,
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
    overrides: DiscoveryOverrides,
) -> DiscoveredDocs:
    docs: list[str] = []
    adrs: list[str] = []
    omitted: list[str] = []
    excluded: dict[str, str] = {}
    budget_chars = max_tokens * 4
    used_chars = 0
    immutable_prefixes = tuple(_normalize_path(path) for path in project.docs.immutable_paths)
    rules = _discovery_rules(project, overrides)

    for configured in sorted(project.docs.paths):
        path = repo_root / configured
        candidates = _doc_candidates(repo_root, path, rules=rules, excluded=excluded)
        for candidate in candidates:
            relative = _relative(repo_root, candidate)
            reason = _exclusion_reason(relative, rules)
            if reason is not None:
                excluded.setdefault(relative, reason)
                continue
            size = candidate.stat().st_size
            if used_chars + size > budget_chars:
                omitted.append(relative)
                continue
            used_chars += size
            if _is_immutable(relative, immutable_prefixes):
                adrs.append(relative)
            else:
                docs.append(relative)

    return DiscoveredDocs(
        docs=sorted(set(docs)),
        adrs=sorted(set(adrs)),
        omitted=sorted(set(omitted)),
        excluded=[
            {"path": path, "reason": reason}
            for path, reason in sorted(excluded.items(), key=lambda item: item[0])
        ],
        rules={
            "default_exclude": list(DEFAULT_DISCOVERY_EXCLUDE),
            "project_include": list(project.docs.discovery_include),
            "project_exclude": list(project.docs.discovery_exclude),
            "user_include": list(overrides.include),
            "user_exclude": list(overrides.exclude),
        },
    )


def _discovery_rules(
    project: ProjectProfile,
    overrides: DiscoveryOverrides,
) -> dict[str, tuple[str, ...]]:
    return {
        "include": tuple(
            _normalize_path(pattern)
            for pattern in (*project.docs.discovery_include, *overrides.include)
        ),
        "exclude": tuple(
            _normalize_path(pattern)
            for pattern in (
                *DEFAULT_DISCOVERY_EXCLUDE,
                *project.docs.discovery_exclude,
                *overrides.exclude,
            )
        ),
    }


def _doc_candidates(
    repo_root: Path,
    path: Path,
    *,
    rules: dict[str, tuple[str, ...]],
    excluded: dict[str, str],
) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        return []
    candidates: list[Path] = []
    include_rules = rules["include"]
    for root, dirs, files in os.walk(path):
        current = Path(root)
        if not include_rules:
            kept_dirs: list[str] = []
            for dirname in dirs:
                directory = current / dirname
                relative = _relative(repo_root, directory)
                reason = _exclusion_reason(f"{relative}/", rules)
                if reason is None:
                    kept_dirs.append(dirname)
                else:
                    excluded.setdefault(relative, reason)
            dirs[:] = kept_dirs
        for filename in files:
            candidate = current / filename
            if candidate.suffix.lower() in {".md", ".mdx", ".txt"}:
                candidates.append(candidate)
    return sorted(candidates)


def _exclusion_reason(path: str, rules: dict[str, tuple[str, ...]]) -> str | None:
    normalized = _normalize_path(path)
    if _matches_any(normalized, rules["include"]):
        return None
    for pattern in rules["exclude"]:
        if _path_matches(pattern, normalized):
            return f"excluded by discovery rule: {pattern}"
    return None


def _matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(_path_matches(pattern, path) for pattern in patterns)


def _path_matches(pattern: str, path: str) -> bool:
    normalized_pattern = _normalize_path(pattern)
    normalized_path = _normalize_path(path)
    if fnmatch.fnmatchcase(normalized_path, normalized_pattern):
        return True
    if normalized_pattern.startswith("**/") and normalized_pattern.endswith("/**"):
        directory = normalized_pattern.removeprefix("**/").removesuffix("/**")
        return (
            normalized_path == directory
            or normalized_path.endswith(f"/{directory}")
            or f"/{directory}/" in normalized_path
        )
    if normalized_pattern.endswith("/**"):
        prefix = normalized_pattern.removesuffix("/**")
        return normalized_path == prefix or normalized_path.startswith(f"{prefix}/")
    return False


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


def _github_state(
    adapter: GitHubReadAdapter | None,
    project: ProjectProfile,
    repo_state: dict[str, Any],
) -> dict[str, Any]:
    if adapter is None:
        return {"status": "not_loaded"}
    return adapter.case_file_state(
        remote=project.repo.remote,
        ref=str(repo_state["head"]),
    )


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
    github_state: dict[str, Any],
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
    ]
    if github_state.get("status") != "loaded":
        assumptions.append(
            Assumption(
                id=f"assumption_{task.id}_github_not_loaded",
                task_id=task.id,
                statement="No GitHub issue or pull request state was loaded into this case file.",
                rationale=_github_assumption_rationale(github_state),
                confidence=1.0,
                status="open",
            )
        )
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


def _github_assumption_rationale(github_state: dict[str, Any]) -> str:
    status = github_state.get("status")
    if status == "not_configured":
        return "Project remote is not configured as a GitHub repository."
    if status == "error":
        warnings = github_state.get("warnings")
        if isinstance(warnings, list) and warnings:
            return f"GitHub read adapter could not load state: {warnings[0]}"
        return "GitHub read adapter could not load state."
    return "GitHub read adapter was not configured for this case file build."


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
    excluded_docs: list[dict[str, str]],
    discovery_rules: dict[str, list[str]],
    evidence: list[EvidenceReference],
    assumptions: list[Assumption],
) -> dict[str, Any]:
    return {
        "max_tokens": max_tokens,
        "estimated_tokens": _estimate_tokens(docs + adrs),
        "docs_included": len(docs),
        "adrs_included": len(adrs),
        "docs_omitted": omitted_docs,
        "docs_excluded": excluded_docs,
        "discovery_rules": discovery_rules,
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
