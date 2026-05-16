from datetime import UTC, datetime
from pathlib import Path

import pytest

from craik.contracts.models import (
    CapabilityGrant,
    CapabilityTarget,
    IntentLock,
    RunnerMetadata,
)
from craik.runtime.loop import (
    FixtureStepRunner,
    LoopMaxIterationsError,
    LoopStep,
    SingleAgentLoopExecutor,
)
from craik.runtime.memory import LocalMemoryStore
from craik.runtime.paths import ensure_craik_home
from craik.runtime.policy import generate_policy_envelope
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


def test_fixture_loop_completes_and_records_side_effect_receipt(store: LocalStore) -> None:
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=FixtureStepRunner(),
    )

    result = executor.execute(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy=generate_policy_envelope(task_id="task_docs_reconcile", actor="runner:fixture"),
        runner_metadata=_runner(),
        grants=[_shell_grant()],
        started_at=datetime(2026, 5, 16, 12, 0, tzinfo=UTC),
    )

    assert result.run.status == "completed"
    assert result.run.phase == "stop"
    assert result.run.iteration == 4
    assert [step.phase for step in result.step_results] == [
        "plan",
        "act",
        "observe",
        "evaluate",
    ]
    assert result.receipts[0].result.status == "passed"
    assert store.get_receipt(result.receipts[0].id) == result.receipts[0]
    assert len(store.list_run_outputs()) == 4


def test_loop_blocks_before_side_effect_when_policy_denies(store: LocalStore) -> None:
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=FixtureStepRunner(),
    )

    result = executor.execute(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy=generate_policy_envelope(task_id="task_docs_reconcile", actor="runner:fixture"),
        runner_metadata=_runner(),
        grants=[],
    )

    assert result.run.status == "blocked"
    assert result.run.stop_reason == "shell execution requires matching capability grant"
    assert [step.phase for step in result.step_results] == ["plan"]
    assert result.receipts[0].result.status == "denied"
    assert store.get_receipt(result.receipts[0].id) == result.receipts[0]


def test_loop_stops_on_runner_failure(store: LocalStore) -> None:
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=FixtureStepRunner(statuses=["completed", "failed"]),
    )

    result = executor.execute(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy=generate_policy_envelope(task_id="task_docs_reconcile", actor="runner:fixture"),
        runner_metadata=_runner(),
        grants=[_shell_grant()],
    )

    assert result.run.status == "failed"
    assert result.run.phase == "stop"
    assert [step.status for step in result.step_results] == ["completed", "failed"]
    assert result.run.stop_reason == "Fixture act step failed."


def test_loop_enforces_max_iterations(store: LocalStore) -> None:
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=FixtureStepRunner(),
    )

    with pytest.raises(LoopMaxIterationsError, match="max iterations 1 reached"):
        executor.execute(
            task_id="task_docs_reconcile",
            case_file_id="case_docs_reconcile",
            policy=generate_policy_envelope(
                task_id="task_docs_reconcile",
                actor="runner:fixture",
            ),
            runner_metadata=_runner(),
            grants=[_shell_grant()],
            max_iterations=1,
        )


def test_loop_enforces_intent_stop_condition_before_step(store: LocalStore) -> None:
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=FixtureStepRunner(),
    )

    result = executor.execute(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy=generate_policy_envelope(task_id="task_docs_reconcile", actor="runner:fixture"),
        runner_metadata=_runner(),
        intent_lock=IntentLock(
            id="intent_docs_reconcile",
            task_id="task_docs_reconcile",
            original_request="Review documentation.",
            objective="Stay within docs reconciliation.",
            accepted_interpretation="Only reconcile docs.",
            stop_conditions=["scope changed"],
            created_at=datetime(2026, 5, 16, 12, 0, tzinfo=UTC),
        ),
        steps=[
            LoopStep(
                phase="plan",
                input_prompt="Plan.",
                context={"trigger_stop_condition": "scope changed"},
            )
        ],
    )

    assert result.run.status == "blocked"
    assert result.step_results == []
    assert result.run.stop_reason == "intent stop condition triggered: scope changed"


def _runner() -> RunnerMetadata:
    return RunnerMetadata(
        id="runner_fixture",
        name="Fixture Runner",
        adapter="fixture",
        adapter_version="0.1.0",
        mode="fixture",
        capabilities=["prompt.read", "result.structured", "shell.execute"],
        metadata={"contract_test": True},
    )


def _shell_grant() -> CapabilityGrant:
    return CapabilityGrant(
        id="grant_fixture_shell",
        task_id="task_docs_reconcile",
        capability="shell.execute",
        target=CapabilityTarget(paths=["fixture-action"]),
        operations=["execute"],
        reason="Allow deterministic fixture action.",
        approved_by="user:maintainer",
    )
