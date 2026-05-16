import json
from datetime import UTC, datetime
from pathlib import Path

from typer.testing import CliRunner

from craik.cli import app, package_version
from craik.contracts.models import CapabilityReceipt, ReceiptResult
from craik.runtime.paths import ensure_craik_home
from craik.runtime.receipts import ReceiptStore
from craik.runtime.store import LocalStore

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


def test_task_and_case_commands_round_trip(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "adr").mkdir(parents=True)
    (repo / "README.md").write_text("# Repo\n")
    (repo / "docs" / "guide.md").write_text("# Guide\n")
    (repo / "docs" / "adr" / "0001-record.md").write_text("# ADR\n")
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "add", "README.md", "docs")
    _run_git(repo, "commit", "-m", "initial")
    home = tmp_path / "home"

    project = runner.invoke(
        app,
        ["project", "add", str(repo), "--name", "Example"],
        env={"CRAIK_HOME": str(home)},
    )
    task = runner.invoke(
        app,
        [
            "task",
            "create",
            "--project",
            "Example",
            "--title",
            "Review docs",
            "--objective",
            "Review docs against implementation.",
            "--mode",
            "review",
        ],
        env={"CRAIK_HOME": str(home)},
    )
    built = runner.invoke(
        app,
        ["case", "build", "task_review_docs"],
        env={"CRAIK_HOME": str(home)},
    )
    shown = runner.invoke(
        app,
        ["case", "show", "task_review_docs"],
        env={"CRAIK_HOME": str(home)},
    )

    assert project.exit_code == 0
    assert task.exit_code == 0
    assert built.exit_code == 0
    assert shown.exit_code == 0
    assert json.loads(task.stdout)["id"] == "task_review_docs"
    assert json.loads(built.stdout)["adrs"] == ["docs/adr/0001-record.md"]
    assert json.loads(shown.stdout)["id"] == "case_review_docs"


def test_case_build_reports_missing_task(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["case", "build", "task_missing"],
        env={"CRAIK_HOME": str(tmp_path / "home")},
    )

    assert result.exit_code != 0
    assert "unknown task: task_missing" in result.output


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


def test_receipts_commands_list_and_show_persisted_receipts(tmp_path: Path) -> None:
    home = tmp_path / "home"
    _seed_receipt(
        home,
        _receipt(
            "receipt_docs",
            task_id="task_docs",
            metadata={
                "policy_envelope_id": "policy_docs",
                "handoff_ids": ["handoff_docs"],
            },
        ),
    )
    _seed_receipt(home, _receipt("receipt_other", task_id="task_other"))

    listed = runner.invoke(
        app,
        ["receipts", "list", "--task-id", "task_docs"],
        env={"CRAIK_HOME": str(home)},
    )
    shown = runner.invoke(
        app,
        ["receipts", "show", "receipt_docs"],
        env={"CRAIK_HOME": str(home)},
    )
    by_policy = runner.invoke(
        app,
        ["receipts", "list", "--policy-id", "policy_docs"],
        env={"CRAIK_HOME": str(home)},
    )
    by_handoff = runner.invoke(
        app,
        ["receipts", "list", "--handoff-id", "handoff_docs"],
        env={"CRAIK_HOME": str(home)},
    )

    assert listed.exit_code == 0
    assert shown.exit_code == 0
    assert by_policy.exit_code == 0
    assert by_handoff.exit_code == 0
    assert [receipt["id"] for receipt in json.loads(listed.stdout)] == ["receipt_docs"]
    assert json.loads(shown.stdout)["id"] == "receipt_docs"
    assert [receipt["id"] for receipt in json.loads(by_policy.stdout)] == ["receipt_docs"]
    assert [receipt["id"] for receipt in json.loads(by_handoff.stdout)] == ["receipt_docs"]


def test_receipts_show_reports_missing_receipt(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["receipts", "show", "receipt_missing"],
        env={"CRAIK_HOME": str(tmp_path / "home")},
    )

    assert result.exit_code != 0
    assert "unknown receipt: receipt_missing" in result.output


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


def _seed_receipt(home: Path, receipt: CapabilityReceipt) -> None:
    paths = ensure_craik_home({"CRAIK_HOME": str(home)})
    store = LocalStore.from_paths(paths)
    try:
        store.initialize()
        ReceiptStore(store).record_receipt(receipt)
    finally:
        store.close()


def _receipt(
    receipt_id: str,
    *,
    task_id: str,
    metadata: dict[str, object] | None = None,
) -> CapabilityReceipt:
    return CapabilityReceipt(
        id=receipt_id,
        task_id=task_id,
        actor="agent:codex",
        capability="shell.test",
        target="uv run pytest",
        policy_profile="strict",
        fail_open=False,
        reason="Validate receipt behavior.",
        result=ReceiptResult(
            status="passed",
            summary="Command completed.",
            metadata=metadata or {},
        ),
        redacted=True,
        created_at=datetime(2026, 5, 15, 12, 0, tzinfo=UTC),
    )
