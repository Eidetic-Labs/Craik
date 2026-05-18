from datetime import UTC, datetime
from pathlib import Path

import pytest

from craik.contracts.models import RunnerMetadata, RunnerStepResult
from craik.runtime.memory.memory import LocalMemoryStore
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore
from craik.runtime.work.run_outputs import RunOutputProposalSpec, RunOutputRecorder, run_output_id


@pytest.fixture
def store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_capture_step_result_persists_redacted_output_and_proposal(
    store: LocalStore,
) -> None:
    recorder = RunOutputRecorder(store, LocalMemoryStore(store))
    step = _step_result(
        observed_output={"finding": "Use local state.", "api_token": "secret-value"},
        summary="Local state is available.",
    )

    capture = recorder.capture_step_result(
        step,
        proposal_specs=[
            RunOutputProposalSpec(
                entity="repo:eidetic-labs/craik",
                relation="craik:run_output",
                value="Local state is available.",
                handoff_id="handoff_docs_reconcile",
            )
        ],
        captured_at=datetime(2026, 5, 16, 12, 0, tzinfo=UTC),
    )

    assert capture.skipped_reasons == []
    assert capture.output.id == run_output_id(step.run_id, step.id)
    assert capture.output.observed_output["api_token"] == "[REDACTED]"
    assert capture.output.memory_proposal_ids == [capture.proposals[0].id]
    assert store.get_run_output(capture.output.id) == capture.output
    proposal = store.get_proposal(capture.proposals[0].id)
    assert proposal is not None
    assert proposal.run_id == step.run_id
    assert proposal.step_id == step.id
    assert proposal.handoff_id == "handoff_docs_reconcile"
    assert proposal.evidence[0].locator == f"{capture.output.id}#{step.id}"


def test_blocked_step_persists_output_but_skips_proposals(store: LocalStore) -> None:
    recorder = RunOutputRecorder(store, LocalMemoryStore(store))
    step = _step_result(status="blocked", diagnostics=["approval required"])

    capture = recorder.capture_step_result(
        step,
        proposal_specs=[
            RunOutputProposalSpec(
                entity="repo:eidetic-labs/craik",
                relation="craik:run_output",
            )
        ],
    )

    assert capture.proposals == []
    assert capture.output.memory_proposal_ids == []
    assert capture.skipped_reasons == ["step status blocked does not create memory proposals"]
    assert store.get_run_output(capture.output.id) == capture.output


def test_missing_proposal_specs_records_skipped_reason(store: LocalStore) -> None:
    recorder = RunOutputRecorder(store, LocalMemoryStore(store))

    capture = recorder.capture_step_result(_step_result(), proposal_specs=[])

    assert capture.proposals == []
    assert capture.skipped_reasons == ["no memory proposal specs supplied"]


def test_capture_step_result_exposes_stream_chunks(store: LocalStore) -> None:
    recorder = RunOutputRecorder(store, LocalMemoryStore(store))

    capture = recorder.capture_step_result(
        _step_result(observed_output={"stream_chunks": ["Hel", "lo", "!"]}),
    )

    assert capture.chunks == ["Hel", "lo", "!"]
    assert capture.output.observed_output["stream_chunks"] == ["Hel", "lo", "!"]


def _step_result(
    *,
    status: str = "completed",
    observed_output: dict[str, object] | None = None,
    summary: str = "Step completed.",
    diagnostics: list[str] | None = None,
) -> RunnerStepResult:
    return RunnerStepResult(
        id="runner_step_result_docs_reconcile_plan",
        request_id="runner_step_request_docs_reconcile_plan",
        run_id="run_docs_reconcile",
        task_id="task_docs_reconcile",
        phase="plan",
        runner=RunnerMetadata(
            id="runner_fixture",
            name="Fixture Runner",
            adapter="fixture",
            adapter_version="0.1.0",
            mode="fixture",
            capabilities=["prompt.read", "result.structured"],
            metadata={"contract_test": True},
        ),
        status=status,
        summary=summary,
        observed_output=observed_output or {"finding": "Use local state."},
        diagnostics=diagnostics or [],
        receipt_ids=["receipt_runner_fixture"],
        artifacts=["case_docs_reconcile"],
        created_at=datetime(2026, 5, 16, 11, 0, tzinfo=UTC),
    )
