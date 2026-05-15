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

