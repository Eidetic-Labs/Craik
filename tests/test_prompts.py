import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from craik.contracts.models import CapabilityGrant, CapabilityTarget
from craik.runtime.paths import ensure_craik_home
from craik.runtime.projects.project_registry import ProjectRegistry
from craik.runtime.projects.prompts import (
    PromptCaseFileNotFoundError,
    PromptCompiler,
    PromptTaskNotFoundError,
)
from craik.runtime.store import LocalStore
from craik.runtime.work.case_files import CaseFileAssembler
from craik.runtime.work.tasks import create_task


@pytest.fixture
def store(tmp_path: Path):
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_prompt_compiler_is_deterministic_and_persisted(
    tmp_path: Path,
    store: LocalStore,
) -> None:
    repo = _repo(tmp_path)
    project = ProjectRegistry(store).add_project(repo, name="Example")
    task = create_task(
        store,
        title="Review docs",
        objective="Review docs against implementation.",
        project_id=project.id,
        mode="review",
        constraints=["Do not edit ADRs."],
        expected_outputs=["runner_result", "handoff"],
    )
    CaseFileAssembler(store).build(task.id)
    store.put_capability_grant(
        CapabilityGrant(
            id="grant_docs_write",
            task_id=task.id,
            capability="repo.write.docs",
            target=CapabilityTarget(repo="Example", paths=["docs/**"], exclude=["docs/adr/**"]),
            operations=["write"],
            expires_at=datetime(2026, 5, 17, tzinfo=UTC),
            reason="Docs update approval.",
            approved_by="user:maintainer",
        )
    )
    compiler = PromptCompiler(store)

    first = compiler.compile(task.id, runner_id="codex")
    second = compiler.compile(task.id, runner_id="codex")

    assert first == second
    assert first.id == "prompt_review_docs_codex"
    assert first.runner_id == "codex"
    assert first.runner_mode == "live"
    assert first.capability_grant_ids == ["grant_docs_write"]
    assert "Policy id: policy_task_review_docs" in first.prompt
    assert "grant_docs_write: repo.write.docs" in first.prompt
    assert "Document excluded from discovery" in first.prompt
    assert "Memory facts were not loaded into the case file." in first.context_omissions
    loaded = store.get_compiled_prompt(first.id)
    assert loaded == first


def test_prompt_compiler_surfaces_runner_policy_boundaries(
    tmp_path: Path,
    store: LocalStore,
) -> None:
    repo = _repo(tmp_path)
    project = ProjectRegistry(store).add_project(repo, name="Example")
    task = create_task(
        store,
        title="Summarize docs",
        objective="Summarize documentation.",
        project_id=project.id,
        mode="review",
    )
    CaseFileAssembler(store).build(task.id)

    compiled = PromptCompiler(store).compile(task.id, runner_id="gemini")

    assert "Runner id: gemini" in compiled.prompt
    assert "Trust level: low" in compiled.prompt
    assert "memory.write: unsupported" in compiled.prompt
    assert "Do not treat assumptions, stale risks, or omitted context as facts." in compiled.prompt


def test_prompt_compiler_requires_task_and_case_file(
    tmp_path: Path,
    store: LocalStore,
) -> None:
    repo = _repo(tmp_path)
    project = ProjectRegistry(store).add_project(repo, name="Example")
    task = create_task(
        store,
        title="No case",
        objective="No case exists.",
        project_id=project.id,
    )

    with pytest.raises(PromptTaskNotFoundError):
        PromptCompiler(store).compile("task_missing", runner_id="codex")
    with pytest.raises(PromptCaseFileNotFoundError):
        PromptCompiler(store).compile(task.id, runner_id="codex")


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs" / "adr").mkdir(parents=True)
    (repo / "README.md").write_text("# Repo\n")
    (repo / "docs" / "guide.md").write_text("# Guide\n")
    (repo / "docs" / "adr" / "0001-record.md").write_text("# ADR\n")
    (repo / "docs" / "archive").mkdir()
    (repo / "docs" / "archive" / "old.md").write_text("# Old\n")
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "add", "README.md", "docs")
    _run_git(repo, "commit", "-m", "initial")
    return repo


def _run_git(repo: Path, *args: str) -> None:
    subprocess_args = ["git", *args]
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Craik Tests",
        "GIT_AUTHOR_EMAIL": "tests@craik.local",
        "GIT_COMMITTER_NAME": "Craik Tests",
        "GIT_COMMITTER_EMAIL": "tests@craik.local",
    }
    subprocess.run(
        subprocess_args,
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
