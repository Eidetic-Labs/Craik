import subprocess
from pathlib import Path

import pytest

from craik.runtime.case_files import CaseFileAssembler, ProjectNotFoundError, TaskNotFoundError
from craik.runtime.paths import ensure_craik_home
from craik.runtime.project_registry import ProjectRegistry
from craik.runtime.store import LocalStore
from craik.runtime.tasks import create_task


@pytest.fixture
def store(tmp_path: Path):
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_case_file_build_is_deterministic_and_persisted(
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
    )
    assembler = CaseFileAssembler(store)

    first = assembler.build(task.id)
    second = assembler.build(task.id)

    assert first == second
    loaded = assembler.latest_for_task(task.id)
    assert loaded is not None
    assert loaded.model_dump(mode="json", by_alias=True) == first.model_dump(
        mode="json",
        by_alias=True,
    )
    assert first.id == "case_review_docs"
    assert first.policy_envelope_id == "policy_task_review_docs"
    assert first.docs == ["README.md", "docs/guide.md"]
    assert first.adrs == ["docs/adr/0001-record.md"]
    assert first.repo_state["status"] == "clean"
    assert first.context_budget["max_tokens"] == 24000
    assert first.context_budget["docs_included"] == 2
    assert first.context_budget["adrs_included"] == 1


def test_case_file_labels_immutable_evidence(tmp_path: Path, store: LocalStore) -> None:
    repo = _repo(tmp_path)
    project = ProjectRegistry(store).add_project(repo, name="Example")
    task = create_task(
        store,
        title="Check ADRs",
        objective="Check immutable docs.",
        project_id=project.id,
    )

    case_file = CaseFileAssembler(store).build(task.id)

    immutable = [
        evidence
        for evidence in case_file.evidence
        if evidence.locator == "docs/adr/0001-record.md"
    ]
    assert immutable
    assert immutable[0].metadata["immutable"] is True


def test_case_file_tracks_missing_context_as_assumptions(
    tmp_path: Path,
    store: LocalStore,
) -> None:
    repo = _repo(tmp_path)
    project = ProjectRegistry(store).add_project(repo, name="Example", docs_paths=("missing/",))
    task = create_task(
        store,
        title="Missing docs",
        objective="Build case with missing docs.",
        project_id=project.id,
    )

    case_file = CaseFileAssembler(store).build(task.id)

    statements = {assumption.statement for assumption in case_file.assumptions}
    assert "No memory facts were loaded into this case file." in statements
    assert "No GitHub issue or pull request state was loaded into this case file." in statements
    assert "No mutable documentation files were discovered for this project." in statements
    assert case_file.github_state == {"status": "not_loaded"}
    assert "Case file contains open assumptions" in case_file.stale_risks[-1]


def test_case_file_reports_omitted_docs_from_context_budget(
    tmp_path: Path,
    store: LocalStore,
) -> None:
    repo = _repo(tmp_path)
    (repo / "docs" / "long.md").write_text("x" * 100)
    _run_git(repo, "add", "docs/long.md")
    _run_git(repo, "commit", "-m", "add long doc")
    project = ProjectRegistry(store).add_project(repo, name="Example")
    task = create_task(
        store,
        title="Small budget",
        objective="Build case with a small context budget.",
        project_id=project.id,
    )

    case_file = CaseFileAssembler(store).build(task.id, max_tokens=1)

    assert "docs/long.md" in case_file.context_budget["docs_omitted"]
    assert any("omitted from the case file" in item.statement for item in case_file.assumptions)


def test_case_file_errors_for_missing_task_or_project(store: LocalStore) -> None:
    assembler = CaseFileAssembler(store)

    with pytest.raises(TaskNotFoundError, match="unknown task"):
        assembler.build("task_missing")

    task = create_task(
        store,
        title="Bad project",
        objective="Missing project.",
        project_id="project_missing",
    )

    with pytest.raises(ProjectNotFoundError, match="unknown project"):
        assembler.build(task.id)


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs" / "adr").mkdir(parents=True)
    (repo / "README.md").write_text("# Example\n")
    (repo / "docs" / "guide.md").write_text("# Guide\n")
    (repo / "docs" / "adr" / "0001-record.md").write_text("# ADR\n")
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "add", "README.md", "docs")
    _run_git(repo, "commit", "-m", "initial")
    return repo


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ("git", *args),
        cwd=repo,
        check=True,
        env={
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_AUTHOR_NAME": "Craik Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Craik Test",
        },
    )
