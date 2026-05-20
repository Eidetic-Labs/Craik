from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from craik.contracts.models import (
    CapabilityGrant,
    CapabilityTarget,
    IntentLock,
    RunnerMetadata,
    RunnerStepRequest,
    RunnerStepResult,
)
from craik.runtime.auth.operator import OperatorSession, OperatorSessionStore
from craik.runtime.memory.memory import LocalMemoryStore
from craik.runtime.paths import ensure_craik_home
from craik.runtime.policy.policy import generate_policy_envelope
from craik.runtime.store import LocalStore
from craik.runtime.work.loop import (
    FixtureStepRunner,
    LoopMaxIterationsError,
    LoopStep,
    LoopTimeBudgetExceededError,
    SingleAgentLoopExecutor,
)


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


def test_loop_enforces_wall_clock_budget_before_next_step(store: LocalStore) -> None:
    runner = RecordingStepRunner()
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=runner,
    )

    with pytest.raises(LoopTimeBudgetExceededError, match="wall-clock budget 1s exceeded"):
        executor.execute(
            task_id="task_docs_reconcile",
            case_file_id="case_docs_reconcile",
            policy=generate_policy_envelope(
                task_id="task_docs_reconcile",
                actor="runner:fixture",
            ),
            runner_metadata=_runner(),
            steps=[LoopStep(phase="plan", input_prompt="Plan.")],
            wall_clock_budget_seconds=1,
            started_at=datetime.now(UTC) - timedelta(seconds=5),
        )

    run = store.list_task_runs()[0]
    assert run.status == "interrupted"
    assert run.iteration == 0
    assert run.wall_clock_budget_seconds == 1
    assert run.stop_reason == "wall-clock budget 1s exceeded"
    assert runner.requests == []


def test_loop_resumes_interrupted_run_from_completed_phase_boundary(
    store: LocalStore,
) -> None:
    runner = RecordingStepRunner()
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=runner,
    )
    steps = [
        LoopStep(phase="plan", input_prompt="Plan."),
        LoopStep(
            phase="act",
            input_prompt="Act.",
            side_effect_capability="shell.execute",
            side_effect_target="fixture-action",
        ),
        LoopStep(phase="observe", input_prompt="Observe."),
        LoopStep(phase="evaluate", input_prompt="Evaluate."),
    ]

    with pytest.raises(LoopMaxIterationsError, match="max iterations 2 reached"):
        executor.execute(
            task_id="task_docs_reconcile",
            case_file_id="case_docs_reconcile",
            policy=generate_policy_envelope(
                task_id="task_docs_reconcile",
                actor="runner:fixture",
            ),
            runner_metadata=_runner(),
            grants=[_shell_grant()],
            steps=steps,
            max_iterations=2,
        )

    interrupted = store.list_task_runs()[0]
    assert interrupted.status == "interrupted"
    assert interrupted.iteration == 2
    assert interrupted.completed_step_keys == [
        f"{interrupted.id}:1:plan",
        f"{interrupted.id}:2:act",
    ]
    assert len(store.list_run_outputs()) == 2
    assert len(store.list_receipts()) == 1

    resumed = executor.execute(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy=generate_policy_envelope(task_id="task_docs_reconcile", actor="runner:fixture"),
        runner_metadata=_runner(),
        grants=[_shell_grant()],
        steps=steps,
        max_iterations=5,
        resume_run_id=interrupted.id,
    )

    assert resumed.run.status == "completed"
    assert resumed.run.iteration == 4
    assert [request.phase for request in runner.requests] == [
        "plan",
        "act",
        "observe",
        "evaluate",
    ]
    assert [request.context["idempotency_key"] for request in runner.requests] == [
        f"{interrupted.id}:1:plan",
        f"{interrupted.id}:2:act",
        f"{interrupted.id}:3:observe",
        f"{interrupted.id}:4:evaluate",
    ]
    assert [capture.output.phase for capture in resumed.output_captures] == [
        "plan",
        "act",
        "observe",
        "evaluate",
    ]
    assert resumed.output_captures[0].skipped_reasons == [
        "step already completed; reused durable output"
    ]
    assert len(store.list_run_outputs()) == 4
    assert len(store.list_receipts()) == 1


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


def test_loop_denies_operator_missing_required_group(
    store: LocalStore,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CRAIK_HOME", str(tmp_path / "auth_home"))
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=FixtureStepRunner(),
    )
    policy = generate_policy_envelope(task_id="task_docs_reconcile", actor="runner:fixture")
    policy = policy.model_copy(
        update={"required_operator": True, "allowed_operator_groups": ["prod-deploy"]}
    )

    result = executor.execute(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy=policy,
        runner_metadata=_runner(),
        grants=[_shell_grant()],
    )

    assert result.run.status == "blocked"
    assert result.run.stop_reason == "operator identity required by policy; run craik login"
    assert result.step_results == []
    assert result.receipts[0].capability == "operator.identity"
    assert result.receipts[0].result.status == "denied"
    assert store.get_receipt(result.receipts[0].id) == result.receipts[0]


def test_loop_passes_operator_policy_match_to_runner_context(
    store: LocalStore,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    auth_home = tmp_path / "auth_home"
    monkeypatch.setenv("CRAIK_HOME", str(auth_home))
    OperatorSessionStore(auth_home).put(
        OperatorSession(
            subject="operator-123",
            email="operator@example.test",
            display_name="Operator",
            groups=["platform", "prod-deploy"],
            issuer="https://issuer.example.test",
            id_token_jti="token-1",
            expires_at=datetime(2026, 5, 18, tzinfo=UTC),
        )
    )
    runner = RecordingStepRunner()
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=runner,
    )
    policy = generate_policy_envelope(task_id="task_docs_reconcile", actor="runner:fixture")
    policy = policy.model_copy(
        update={"required_operator": True, "allowed_operator_groups": ["prod-deploy"]}
    )

    result = executor.execute(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy=policy,
        runner_metadata=_runner(),
        grants=[_shell_grant()],
        steps=[LoopStep(phase="act", input_prompt="Act.")],
        max_iterations=2,
    )

    assert result.run.status == "completed"
    assert runner.requests[0].context["operator_policy"]["matched_operator_group"] == (
        "prod-deploy"
    )


def test_loop_executes_tool_call_and_replays_tool_result(store: LocalStore) -> None:
    runner = ToolCallStepRunner()
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=runner,
    )

    result = executor.execute(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy=generate_policy_envelope(task_id="task_docs_reconcile", actor="runner:fixture"),
        runner_metadata=_runner(),
        grants=[_shell_grant()],
        steps=[LoopStep(phase="act", input_prompt="Run the requested tool.")],
        max_iterations=3,
    )

    assert result.run.status == "completed"
    assert result.run.iteration == 2
    assert len(runner.requests) == 2
    assert len(result.step_results) == 2
    assert len(result.output_captures) == 2
    assert result.receipts[0].capability == "shell.execute"
    assert result.receipts[0].result.metadata["command_ref"] == "fixture-action"
    assert store.get_receipt(result.receipts[0].id) == result.receipts[0]
    assert runner.requests[1].context["message_history"][0]["role"] == "tool"
    assert runner.requests[1].context["message_history"][0]["tool_call_id"] == "call_shell"
    assert result.step_results[-1].observed_output["text"] == "tool result consumed"


def test_loop_captures_streaming_chunks(store: LocalStore) -> None:
    runner = StreamingStepRunner(chunks=["Hel", "lo", "!"])
    executor = SingleAgentLoopExecutor(
        store=store,
        memory=LocalMemoryStore(store),
        runner=runner,
    )

    result = executor.execute(
        task_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy=generate_policy_envelope(task_id="task_docs_reconcile", actor="runner:fixture"),
        runner_metadata=_runner(),
        steps=[LoopStep(phase="act", input_prompt="Stream the answer.")],
        max_iterations=2,
    )

    assert result.run.status == "completed"
    assert result.output_captures[0].chunks == ["Hel", "lo", "!"]
    assert result.output_captures[0].output.observed_output["stream_chunks"] == [
        "Hel",
        "lo",
        "!",
    ]
    assert result.output_captures[0].output.observed_output["stream_text"] == "Hello!"
    assert result.step_results[0].observed_output["text"] == "Hello!"


class ToolCallStepRunner:
    def __init__(self) -> None:
        self.requests: list[RunnerStepRequest] = []

    def run_step(
        self,
        request: RunnerStepRequest,
        *,
        stream_callback: Callable[[str], None] | None = None,
    ) -> RunnerStepResult:
        _ = stream_callback
        self.requests.append(request)
        if len(self.requests) == 1:
            return RunnerStepResult(
                id=f"runner_step_result_{request.run_id}_tool_call",
                request_id=request.id,
                run_id=request.run_id,
                task_id=request.task_id,
                phase=request.phase,
                runner=request.runner,
                status="completed",
                summary="Requested a shell tool.",
                observed_output={
                    "tool_calls": [
                        {
                            "id": "call_shell",
                            "name": "shell.execute",
                            "arguments": '{"command_ref":"fixture-action"}',
                        }
                    ]
                },
                created_at=datetime.now(UTC),
            )
        return RunnerStepResult(
            id=f"runner_step_result_{request.run_id}_tool_result",
            request_id=request.id,
            run_id=request.run_id,
            task_id=request.task_id,
            phase=request.phase,
            runner=request.runner,
            status="completed",
            summary="Consumed the tool result.",
            observed_output={"text": "tool result consumed"},
            created_at=datetime.now(UTC),
        )


class RecordingStepRunner:
    def __init__(self) -> None:
        self.requests: list[RunnerStepRequest] = []

    def run_step(
        self,
        request: RunnerStepRequest,
        *,
        stream_callback: Callable[[str], None] | None = None,
    ) -> RunnerStepResult:
        _ = stream_callback
        self.requests.append(request)
        return RunnerStepResult(
            id=f"runner_step_result_{request.run_id}_{request.phase}",
            request_id=request.id,
            run_id=request.run_id,
            task_id=request.task_id,
            phase=request.phase,
            runner=request.runner,
            status="completed",
            summary="Recorded step.",
            observed_output={"phase": request.phase},
            created_at=datetime.now(UTC),
        )


class StreamingStepRunner:
    def __init__(self, *, chunks: list[str]) -> None:
        self.chunks = chunks

    def run_step(
        self,
        request: RunnerStepRequest,
        *,
        stream_callback: Callable[[str], None] | None = None,
    ) -> RunnerStepResult:
        for chunk in self.chunks:
            if stream_callback is not None:
                stream_callback(chunk)
        text = "".join(self.chunks)
        return RunnerStepResult(
            id=f"runner_step_result_{request.run_id}_stream",
            request_id=request.id,
            run_id=request.run_id,
            task_id=request.task_id,
            phase=request.phase,
            runner=request.runner,
            status="completed",
            summary="Streamed the result.",
            observed_output={"text": text},
            created_at=datetime.now(UTC),
        )


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
