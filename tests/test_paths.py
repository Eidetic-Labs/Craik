from pathlib import Path

import pytest

from craik.runtime.paths import (
    CRAIK_HOME_ENV,
    LAYOUT_DIRS,
    ensure_craik_home,
    ensure_project_local_dir,
    owner_only,
    project_local_dir,
    resolve_craik_home,
    resolve_craik_paths,
)


def test_default_home_resolves_to_user_craik_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(CRAIK_HOME_ENV, raising=False)

    assert resolve_craik_home() == Path.home() / ".craik"


def test_env_override_resolves_to_absolute_path(tmp_path: Path) -> None:
    home = tmp_path / "custom-home"

    assert resolve_craik_home({CRAIK_HOME_ENV: str(home)}) == home.resolve()


def test_resolved_paths_include_standard_layout(tmp_path: Path) -> None:
    home = tmp_path / "craik-home"
    paths = resolve_craik_paths({CRAIK_HOME_ENV: str(home)})

    assert paths.home == home.resolve()
    assert [path.name for path in paths.layout_dirs()] == list(LAYOUT_DIRS)
    assert paths.case_files.name == "case-files"


def test_ensure_craik_home_creates_standard_layout(tmp_path: Path) -> None:
    home = tmp_path / "craik-home"
    paths = ensure_craik_home({CRAIK_HOME_ENV: str(home)})

    assert paths.home.is_dir()
    for directory in paths.layout_dirs():
        assert directory.is_dir()


def test_home_and_secrets_are_owner_only_where_supported(tmp_path: Path) -> None:
    home = tmp_path / "craik-home"
    paths = ensure_craik_home({CRAIK_HOME_ENV: str(home)})

    assert owner_only(paths.home)
    assert owner_only(paths.secrets)


def test_project_local_path_resolution_does_not_create_directory(tmp_path: Path) -> None:
    target = project_local_dir(tmp_path)

    assert target == tmp_path / ".craik"
    assert not target.exists()


def test_project_local_dir_requires_explicit_opt_in(tmp_path: Path) -> None:
    with pytest.raises(PermissionError):
        ensure_project_local_dir(tmp_path)

    assert not (tmp_path / ".craik").exists()


def test_project_local_dir_can_be_created_with_explicit_opt_in(tmp_path: Path) -> None:
    target = ensure_project_local_dir(tmp_path, opt_in=True)

    assert target == tmp_path / ".craik"
    assert target.is_dir()
    assert owner_only(target)

