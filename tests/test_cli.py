from typer.testing import CliRunner

from craik.cli import app, package_version

runner = CliRunner()


def test_package_import_exposes_version() -> None:
    assert package_version()


def test_version_option_prints_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == package_version()


def test_version_command_prints_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == package_version()


def test_schema_list_includes_task_request() -> None:
    result = runner.invoke(app, ["schema", "list"])

    assert result.exit_code == 0
    assert "craik.task_request" in result.stdout


def test_schema_show_prints_json_schema() -> None:
    result = runner.invoke(app, ["schema", "show", "craik.task_request"])

    assert result.exit_code == 0
    assert '"title": "TaskRequest"' in result.stdout


def test_home_show_does_not_create_home(tmp_path) -> None:
    home = tmp_path / "craik-home"

    result = runner.invoke(app, ["home", "show"], env={"CRAIK_HOME": str(home)})

    assert result.exit_code == 0
    assert str(home) in result.stdout
    assert not home.exists()


def test_home_init_creates_home_layout(tmp_path) -> None:
    home = tmp_path / "craik-home"

    result = runner.invoke(app, ["home", "init"], env={"CRAIK_HOME": str(home)})

    assert result.exit_code == 0
    assert (home / "config").is_dir()
    assert (home / "secrets").is_dir()
    assert (home / "case-files").is_dir()
