import subprocess
from pathlib import Path

import pytest

from craik.runtime.paths import ensure_craik_home
from craik.runtime.projects.project_registry import (
    NotGitRepositoryError,
    ProjectRegistry,
    detect_default_branch,
    detect_git_root,
    project_id,
)
from craik.runtime.store import LocalStore


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    _run("git", "init", "-b", "main", cwd=repo)
    (repo / "README.md").write_text("# Demo\n")
    (repo / "docs" / "adr").mkdir(parents=True)
    (repo / "docs" / "index.md").write_text("# Docs\n")
    _run("git", "add", ".", cwd=repo)
    _run("git", "commit", "-m", "initial", cwd=repo)
    return repo


def test_detect_git_root_from_nested_path(git_repo: Path) -> None:
    nested = git_repo / "docs"

    assert detect_git_root(nested) == git_repo.resolve()


def test_detect_default_branch(git_repo: Path) -> None:
    assert detect_default_branch(git_repo) == "main"


def test_invalid_repo_path_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(NotGitRepositoryError):
        detect_git_root(tmp_path)


def test_project_id_is_stable_slug() -> None:
    assert project_id("Demo Repo!") == "project_demo-repo"


def test_project_registry_persists_across_store_instances(tmp_path: Path, git_repo: Path) -> None:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    registry = ProjectRegistry(store)

    project = registry.add_project(git_repo, name="Demo")
    store.close()

    reopened = LocalStore.from_paths(paths)
    reopened.initialize()
    try:
        assert ProjectRegistry(reopened).get_project(project.id) == project
        assert ProjectRegistry(reopened).get_project("Demo") == project
    finally:
        reopened.close()


def test_project_registry_round_trips_configured_paths(tmp_path: Path, git_repo: Path) -> None:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    registry = ProjectRegistry(store)

    project = registry.add_project(
        git_repo,
        name="Configured",
        docs_paths=("README.md", "docs/reference/"),
        immutable_paths=("docs/adr/",),
    )

    assert project.docs.paths == ["README.md", "docs/reference/"]
    assert project.docs.immutable_paths == ["docs/adr/"]
    assert registry.get_project("Configured") == project
    store.close()


def test_project_registry_detects_default_docs_and_immutable_paths(
    tmp_path: Path,
    git_repo: Path,
) -> None:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    registry = ProjectRegistry(store)

    project = registry.add_project(git_repo)

    assert project.docs.paths == ["README.md", "docs/"]
    assert project.docs.immutable_paths == ["docs/adr/"]
    assert not (git_repo / ".craik").exists()
    store.close()


def _run(*args: str, cwd: Path) -> None:
    subprocess.run(
        args,
        cwd=cwd,
        check=True,
        env={
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_AUTHOR_NAME": "Craik Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Craik Test",
        },
    )

