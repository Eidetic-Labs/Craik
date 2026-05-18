import subprocess
from pathlib import Path

import pytest

from craik.runtime.projects.git_commands import (
    GitCommandDeniedError,
    run_git,
)


def test_project_git_helper_allows_registered_inspection_commands(tmp_path: Path) -> None:
    subprocess.run(
        ["git", "-C", str(tmp_path), "init"],
        check=True,
        capture_output=True,
        text=True,
    )

    result = run_git(tmp_path, "branch", "--show-current")

    assert result.args == ("git", "-C", str(tmp_path), "branch", "--show-current")
    assert result.returncode == 0
    assert result.stderr == ""


def test_project_git_helper_returns_git_failure_for_allowlisted_command_outside_repo(
    tmp_path: Path,
) -> None:
    result = run_git(tmp_path, "branch", "--show-current")

    assert result.args == ("git", "-C", str(tmp_path), "branch", "--show-current")
    assert result.returncode != 0


@pytest.mark.parametrize(
    "args",
    [
        ("clone", "https://example.invalid/repo.git"),
        ("config", "--global", "credential.helper", "store"),
        ("fetch", "origin"),
        ("remote", "set-url", "origin", "https://example.invalid/repo.git"),
    ],
)
def test_project_git_helper_denies_unregistered_commands(
    tmp_path: Path,
    args: tuple[str, ...],
) -> None:
    with pytest.raises(GitCommandDeniedError, match="not approved"):
        run_git(tmp_path, *args)
