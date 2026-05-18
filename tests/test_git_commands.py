from pathlib import Path

import pytest

from craik.runtime.projects.git_commands import (
    ALLOWED_GIT_ARGS,
    GitCommandDeniedError,
    run_git,
)


def test_project_git_helper_allows_registered_inspection_commands(tmp_path: Path) -> None:
    result = run_git(tmp_path, "branch", "--show-current")

    assert ("branch", "--show-current") in ALLOWED_GIT_ARGS
    assert result.args == ("git", "-C", str(tmp_path), "branch", "--show-current")


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
