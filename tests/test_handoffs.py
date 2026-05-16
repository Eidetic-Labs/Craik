import subprocess
from pathlib import Path

import pytest

from craik.contracts.models import CapabilityReceipt, ReceiptResult
from craik.runtime.case_files import CaseFileAssembler
from craik.runtime.handoffs import HandoffContextError, HandoffWriter, render_markdown
from craik.runtime.paths import ensure_craik_home
from craik.runtime.project_registry import ProjectRegistry
from craik.runtime.receipts import ReceiptStore
from craik.runtime.store import LocalStore
from craik.runtime.tasks import create_task


@pytest.fixture
def store(tmp_path: Path):
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_handoff_writer_creates_structured_handoff(store: LocalStore, tmp_path: Path) -> None:
    task_id = _seed_case(store, tmp_path)
    receipt = _receipt(task_id)
    ReceiptStore(store).record_receipt(receipt)

    handoff = HandoffWriter(store).create(
        task_id=task_id,
        agent="agent:codex",
        summary="Completed docs review.",
        completed_actions=["Reviewed docs."],
        commands_run=["uv run pytest"],
        tests_run=["pytest"],
        next_steps=["Implement handoff reader."],
    )

    assert handoff.id == "handoff_review_docs"
    assert handoff.intent_lock_id == "intent_review_docs"
    assert handoff.receipt_ids == [receipt.id]
    assert handoff.self_audit.schema_validated is True
    assert handoff.self_audit.redaction_reviewed is True
    assert handoff.self_audit.receipts_reviewed is True
    assert handoff.self_audit.assumptions_reviewed is True
    assert handoff.self_audit.validation_recorded is True
    assert "GitHub state was not loaded" in handoff.context_debt[0]
    assert store.get_handoff(handoff.id) == handoff


def test_incomplete_handoff_records_missing_validation_and_policy_exception(
    store: LocalStore,
    tmp_path: Path,
) -> None:
    task_id = _seed_case(store, tmp_path)

    handoff = HandoffWriter(store).create(
        task_id=task_id,
        agent="agent:codex",
        summary="Blocked before validation.",
        status="incomplete",
        policy_exceptions=["No policy exception used."],
    )

    assert handoff.status == "incomplete"
    assert handoff.self_audit.validation_recorded is False
    assert handoff.policy_exceptions == ["No policy exception used."]


def test_markdown_handoff_is_deterministic(store: LocalStore, tmp_path: Path) -> None:
    task_id = _seed_case(store, tmp_path)
    handoff = HandoffWriter(store).create(
        task_id=task_id,
        agent="agent:codex",
        summary="Completed docs review.",
        completed_actions=["Reviewed docs."],
        tests_run=["pytest"],
        next_steps=["Continue with memory backend."],
    )

    markdown = render_markdown(handoff)

    assert markdown.startswith("# Handoff: task_review_docs\n")
    assert "- [x] Schema validated" in markdown
    assert "## Context Debt" in markdown
    assert "- Continue with memory backend." in markdown


def test_handoff_requires_existing_task(store: LocalStore) -> None:
    with pytest.raises(HandoffContextError, match="unknown task"):
        HandoffWriter(store).create(
            task_id="task_missing",
            agent="agent:codex",
            summary="No task.",
        )


def _seed_case(store: LocalStore, tmp_path: Path) -> str:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Repo\n")
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-m", "initial")
    project = ProjectRegistry(store).add_project(repo, name="Example")
    task = create_task(
        store,
        title="Review docs",
        objective="Review docs against implementation.",
        project_id=project.id,
        mode="review",
    )
    CaseFileAssembler(store).build(task.id)
    return task.id


def _receipt(task_id: str) -> CapabilityReceipt:
    from datetime import UTC, datetime

    return CapabilityReceipt(
        id="receipt_pytest",
        task_id=task_id,
        actor="agent:codex",
        capability="shell.test",
        target="uv run pytest",
        policy_profile="strict",
        fail_open=False,
        reason="Validate handoff.",
        result=ReceiptResult(status="passed", summary="Tests passed."),
        redacted=True,
        created_at=datetime(2026, 5, 15, 12, 0, tzinfo=UTC),
    )


def _run_git(repo: Path, *args: str) -> None:
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
