"""Constrained git command helper for project inspection."""

from __future__ import annotations

import subprocess
from pathlib import Path

ALLOWED_GIT_ARGS: frozenset[tuple[str, ...]] = frozenset(
    {
        ("branch", "--show-current"),
        ("config", "--get", "remote.origin.url"),
        ("rev-parse", "--short", "HEAD"),
        ("rev-parse", "--show-toplevel"),
        ("status", "--short"),
        ("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"),
    }
)


class GitCommandDeniedError(ValueError):
    """Raised when project inspection attempts an unapproved git command."""


def run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run one allowlisted git inspection command."""
    if args not in ALLOWED_GIT_ARGS:
        raise GitCommandDeniedError("git command is not approved for project inspection")
    return subprocess.run(
        ("git", "-C", str(cwd), *args),
        check=False,
        text=True,
        capture_output=True,
    )


__all__ = ["ALLOWED_GIT_ARGS", "GitCommandDeniedError", "run_git"]
