"""Project registration and discovery."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from craik.contracts.models import (
    DocsProfile,
    MemoryBackend,
    MemoryProfile,
    MemoryScope,
    ProjectProfile,
    RepoProfile,
)
from craik.runtime.store import LocalStore

DEFAULT_DOC_PATH_CANDIDATES = ("README.md", "docs/")
DEFAULT_IMMUTABLE_PATH_CANDIDATES = ("docs/adr/", "docs/adrs/")


class ProjectRegistryError(RuntimeError):
    """Base error for project registry failures."""


class NotGitRepositoryError(ProjectRegistryError):
    """Raised when a path is not inside a Git repository."""


class ProjectRegistry:
    """Persistent registry for projects Craik can reason about."""

    def __init__(self, store: LocalStore) -> None:
        self.store = store

    def add_project(
        self,
        path: Path,
        *,
        name: str | None = None,
        docs_paths: tuple[str, ...] = (),
        immutable_paths: tuple[str, ...] = (),
        discovery_include: tuple[str, ...] = (),
        discovery_exclude: tuple[str, ...] = (),
        memory_backend: MemoryBackend = "local",
        memory_scope: MemoryScope = "local",
    ) -> ProjectProfile:
        """Register a Git repository and persist its project profile."""
        repo_root = detect_git_root(path)
        project_name = name or repo_root.name
        remote = detect_git_remote(repo_root)
        default_branch = detect_default_branch(repo_root)
        docs = tuple(docs_paths) if docs_paths else detect_docs_paths(repo_root)
        immutable = tuple(immutable_paths) if immutable_paths else detect_immutable_paths(repo_root)

        project = ProjectProfile(
            id=project_id(project_name),
            name=project_name,
            repo=RepoProfile(
                type="git",
                local_path=str(repo_root),
                remote=remote,
                default_branch=default_branch,
            ),
            docs=DocsProfile(
                paths=list(docs),
                immutable_paths=list(immutable),
                discovery_include=list(discovery_include),
                discovery_exclude=list(discovery_exclude),
            ),
            memory=MemoryProfile(backend=memory_backend, scope=memory_scope),
            policies=[],
        )
        self.store.put_project(project)
        return project

    def list_projects(self) -> list[ProjectProfile]:
        """Return registered projects in stable name/id order."""
        return sorted(self.store.list_projects(), key=lambda project: (project.name, project.id))

    def get_project(self, project_id_or_name: str) -> ProjectProfile | None:
        """Find a project by id or name."""
        project = self.store.get_project(project_id_or_name)
        if project is not None:
            return project
        for candidate in self.store.list_projects():
            if candidate.name == project_id_or_name:
                return candidate
        return None


def detect_git_root(path: Path) -> Path:
    """Return the Git repository root for a path."""
    target = path.expanduser().resolve()
    if not target.exists():
        raise NotGitRepositoryError(f"path does not exist: {target}")
    result = _git(target, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        raise NotGitRepositoryError(f"path is not inside a Git repository: {target}")
    return Path(result.stdout.strip()).resolve()


def detect_git_remote(repo_root: Path) -> str | None:
    """Return origin remote URL when configured."""
    result = _git(repo_root, "config", "--get", "remote.origin.url")
    remote = result.stdout.strip()
    return remote or None


def detect_default_branch(repo_root: Path) -> str:
    """Detect the default branch for a Git repository."""
    origin_head = _git(repo_root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if origin_head.returncode == 0 and origin_head.stdout.strip():
        return origin_head.stdout.strip().removeprefix("origin/")

    current = _git(repo_root, "branch", "--show-current")
    if current.returncode == 0 and current.stdout.strip():
        return current.stdout.strip()

    return "main"


def detect_docs_paths(repo_root: Path) -> tuple[str, ...]:
    """Detect conventional documentation paths."""
    return tuple(path for path in DEFAULT_DOC_PATH_CANDIDATES if (repo_root / path).exists())


def detect_immutable_paths(repo_root: Path) -> tuple[str, ...]:
    """Detect conventional immutable documentation paths."""
    return tuple(path for path in DEFAULT_IMMUTABLE_PATH_CANDIDATES if (repo_root / path).exists())


def project_id(name: str) -> str:
    """Create a stable project id from a project name."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"project_{slug or 'unnamed'}"


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", "-C", str(cwd), *args),
        check=False,
        text=True,
        capture_output=True,
    )
