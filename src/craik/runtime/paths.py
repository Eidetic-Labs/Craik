"""Craik local home path resolution and layout creation."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path

CRAIK_HOME_ENV = "CRAIK_HOME"
DEFAULT_HOME_NAME = ".craik"
PROJECT_LOCAL_DIR_NAME = ".craik"

CONFIG_DIR = "config"
SECRETS_DIR = "secrets"
STATE_DIR = "state"
CACHE_DIR = "cache"
LOGS_DIR = "logs"
RECEIPTS_DIR = "receipts"
HANDOFFS_DIR = "handoffs"
CASE_FILES_DIR = "case-files"
PROJECTS_DIR = "projects"

LAYOUT_DIRS: tuple[str, ...] = (
    CONFIG_DIR,
    SECRETS_DIR,
    STATE_DIR,
    CACHE_DIR,
    LOGS_DIR,
    RECEIPTS_DIR,
    HANDOFFS_DIR,
    CASE_FILES_DIR,
    PROJECTS_DIR,
)

OWNER_ONLY_DIR_MODE = 0o700


@dataclass(frozen=True)
class CraikPaths:
    """Resolved Craik local state locations."""

    home: Path
    config: Path
    secrets: Path
    state: Path
    cache: Path
    logs: Path
    receipts: Path
    handoffs: Path
    case_files: Path
    projects: Path

    @classmethod
    def from_home(cls, home: Path) -> CraikPaths:
        """Create a path set from a resolved home directory."""
        return cls(
            home=home,
            config=home / CONFIG_DIR,
            secrets=home / SECRETS_DIR,
            state=home / STATE_DIR,
            cache=home / CACHE_DIR,
            logs=home / LOGS_DIR,
            receipts=home / RECEIPTS_DIR,
            handoffs=home / HANDOFFS_DIR,
            case_files=home / CASE_FILES_DIR,
            projects=home / PROJECTS_DIR,
        )

    def layout_dirs(self) -> tuple[Path, ...]:
        """Return all standard local state directories."""
        return (
            self.config,
            self.secrets,
            self.state,
            self.cache,
            self.logs,
            self.receipts,
            self.handoffs,
            self.case_files,
            self.projects,
        )


def resolve_craik_home(env: dict[str, str] | None = None) -> Path:
    """Resolve Craik's home directory without creating it."""
    values = os.environ if env is None else env
    override = values.get(CRAIK_HOME_ENV)
    if override:
        return Path(override).expanduser().resolve()
    return (Path.home() / DEFAULT_HOME_NAME).resolve()


def resolve_craik_paths(env: dict[str, str] | None = None) -> CraikPaths:
    """Resolve Craik local state paths without creating directories."""
    return CraikPaths.from_home(resolve_craik_home(env))


def ensure_craik_home(env: dict[str, str] | None = None) -> CraikPaths:
    """Create Craik's local home and standard subdirectories."""
    paths = resolve_craik_paths(env)
    _ensure_owner_only_dir(paths.home)
    for directory in paths.layout_dirs():
        _ensure_owner_only_dir(directory)
    return paths


def project_local_dir(project_path: Path) -> Path:
    """Return the opt-in project-local metadata path without creating it."""
    return project_path / PROJECT_LOCAL_DIR_NAME


def ensure_project_local_dir(project_path: Path, *, opt_in: bool = False) -> Path:
    """Create project-local metadata only when explicitly opted in."""
    target = project_local_dir(project_path)
    if not opt_in:
        raise PermissionError("project-local .craik directories require explicit opt-in")
    _ensure_owner_only_dir(target)
    return target


def _ensure_owner_only_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        path.chmod(OWNER_ONLY_DIR_MODE)


def owner_only(path: Path) -> bool:
    """Return whether a path is owner-only on POSIX platforms."""
    if os.name != "posix":
        return True
    mode = stat.S_IMODE(path.stat().st_mode)
    return mode & 0o077 == 0

