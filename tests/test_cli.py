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


def test_project_commands_round_trip_registered_repo(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Repo\n")
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-m", "initial")
    home = tmp_path / "home"

    add = runner.invoke(
        app,
        [
            "project",
            "add",
            str(repo),
            "--name",
            "Example",
            "--docs-path",
            "README.md",
            "--immutable-path",
            "docs/adr/",
        ],
        env={"CRAIK_HOME": str(home)},
    )
    listed = runner.invoke(app, ["project", "list"], env={"CRAIK_HOME": str(home)})
    shown = runner.invoke(app, ["project", "show", "Example"], env={"CRAIK_HOME": str(home)})

    assert add.exit_code == 0
    assert listed.exit_code == 0
    assert shown.exit_code == 0
    assert '"id": "project_example"' in shown.stdout
    assert '"immutable_paths": [' in shown.stdout
    assert not (repo / ".craik").exists()


def test_project_add_rejects_non_repo(tmp_path) -> None:
    result = runner.invoke(
        app,
        ["project", "add", str(tmp_path)],
        env={"CRAIK_HOME": str(tmp_path / "home")},
    )

    assert result.exit_code != 0
    assert "not inside a Git repository" in result.output


def test_policy_show_defaults_to_strict() -> None:
    result = runner.invoke(app, ["policy", "show"])

    assert result.exit_code == 0
    assert '"profile": "strict"' in result.stdout
    assert '"fail_open": false' in result.stdout


def test_policy_show_requires_trusted_local_fail_open_opt_in() -> None:
    result = runner.invoke(app, ["policy", "show", "--profile", "trusted-local"])

    assert result.exit_code != 0
    assert "requires explicit" in result.output


def test_policy_show_can_include_fail_open_receipt() -> None:
    result = runner.invoke(
        app,
        [
            "policy",
            "show",
            "--profile",
            "trusted-local",
            "--trusted-local-fail-open",
            "--include-receipt",
        ],
    )

    assert result.exit_code == 0
    assert '"profile": "trusted-local"' in result.stdout
    assert '"fail_open": true' in result.stdout
    assert '"capability": "policy.fail_open"' in result.stdout


def _run_git(repo, *args: str) -> None:
    import subprocess

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
