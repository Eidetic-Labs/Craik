from datetime import UTC, datetime
from pathlib import Path

import pytest

from craik.runtime.paths import ensure_craik_home
from craik.runtime.runs import (
    RunTransition,
    TaskRunIterationLimitError,
    TaskRunManager,
    TaskRunNotFoundError,
    TaskRunTransitionError,
    task_run_id,
)
from craik.runtime.store import LocalStore


@pytest.fixture
def store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_create_task_run_persists_deterministic_state(store: LocalStore) -> None:
    manager = TaskRunManager(store)
    created_at = datetime(2026, 5, 16, 10, 0, tzinfo=UTC)

    run = manager.create(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy_envelope_id="policy_docs_reconcile",
        intent_lock_id="intent_docs_reconcile",
        runner_id="codex",
        runner_mode="live",
        max_iterations=3,
        created_at=created_at,
    )

    assert run.id == task_run_id("task_docs_reconcile")
    assert run.status == "pending"
    assert run.phase == "plan"
    assert run.started_at == created_at
    assert run.phase_started_at == created_at
    assert store.get_task_run(run.id) == run
    assert store.list_task_runs() == [run]


def test_transition_updates_status_phase_receipts_and_handoff(store: LocalStore) -> None:
    manager = TaskRunManager(store)
    run = manager.create(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy_envelope_id="policy_docs_reconcile",
        runner_id="codex",
        runner_mode="live",
        created_at=datetime(2026, 5, 16, 10, 0, tzinfo=UTC),
    )
    acted_at = datetime(2026, 5, 16, 10, 1, tzinfo=UTC)
    completed_at = datetime(2026, 5, 16, 10, 2, tzinfo=UTC)

    running = manager.transition(
        run.id,
        RunTransition(
            status="running",
            phase="act",
            iteration=1,
            receipt_id="receipt_shell_test",
            at=acted_at,
        ),
    )
    completed = manager.transition(
        run.id,
        RunTransition(
            status="completed",
            phase="stop",
            handoff_id="handoff_docs_reconcile",
            stop_reason="task completed",
            at=completed_at,
        ),
    )

    assert running.status == "running"
    assert running.phase == "act"
    assert running.iteration == 1
    assert running.phase_started_at == acted_at
    assert running.receipt_ids == ["receipt_shell_test"]
    assert completed.status == "completed"
    assert completed.phase == "stop"
    assert completed.ended_at == completed_at
    assert completed.handoff_id == "handoff_docs_reconcile"
    assert completed.stop_reason == "task completed"
    assert store.get_task_run(run.id) == completed


def test_transition_rejects_iteration_limit(store: LocalStore) -> None:
    manager = TaskRunManager(store)
    run = manager.create(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy_envelope_id="policy_docs_reconcile",
        runner_id="codex",
        runner_mode="live",
        max_iterations=1,
        created_at=datetime(2026, 5, 16, 10, 0, tzinfo=UTC),
    )

    with pytest.raises(TaskRunIterationLimitError, match="exceeds max"):
        manager.transition(run.id, RunTransition(iteration=2))


def test_terminal_run_cannot_transition_again(store: LocalStore) -> None:
    manager = TaskRunManager(store)
    run = manager.create(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy_envelope_id="policy_docs_reconcile",
        runner_id="codex",
        runner_mode="live",
        created_at=datetime(2026, 5, 16, 10, 0, tzinfo=UTC),
    )
    manager.transition(
        run.id,
        RunTransition(
            status="failed",
            phase="stop",
            stop_reason="runner failed",
            at=datetime(2026, 5, 16, 10, 1, tzinfo=UTC),
        ),
    )

    with pytest.raises(TaskRunTransitionError, match="already terminal"):
        manager.transition(run.id, RunTransition(phase="observe"))


def test_require_missing_task_run_raises(store: LocalStore) -> None:
    manager = TaskRunManager(store)

    with pytest.raises(TaskRunNotFoundError, match="unknown task run"):
        manager.require("run_missing")
