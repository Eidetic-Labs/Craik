from datetime import UTC, datetime
from typing import cast

import pytest
from pydantic import ValidationError

from craik.contracts.models import (
    RunnerAdapterRequest,
    RunnerAdapterResult,
    RunnerMetadata,
    RunnerResultStatus,
)
from craik.runtime.runners import FixtureRunnerAdapter, RunnerAdapter


def test_fixture_runner_adapter_returns_normalized_result() -> None:
    runner = _runner()
    request = _request(runner)
    result = _result(runner, status="completed")
    adapter = FixtureRunnerAdapter(metadata=runner, result=result)

    returned = adapter.run(request)

    assert isinstance(adapter, RunnerAdapter)
    assert returned == result
    assert returned.runner == runner
    assert returned.outputs["handoff_summary"] == "Docs review completed."


@pytest.mark.parametrize("status", ["completed", "blocked", "failed", "partial"])
def test_runner_adapter_result_accepts_required_statuses(status: str) -> None:
    result = _result(_runner(), status=cast(RunnerResultStatus, status))

    assert result.status == status


def test_runner_adapter_result_rejects_unknown_status() -> None:
    payload = _result(_runner(), status="completed").model_dump(mode="json", by_alias=True)
    payload["status"] = "unknown"

    with pytest.raises(ValidationError):
        RunnerAdapterResult.model_validate(payload)


def test_fixture_runner_adapter_rejects_mismatched_request() -> None:
    runner = _runner()
    request = _request(runner)
    other_runner = RunnerMetadata(
        id="runner_other",
        name="Other",
        adapter="fixture",
        adapter_version="0.1.0",
        mode="fixture",
    )
    adapter = FixtureRunnerAdapter(metadata=other_runner, result=_result(runner))

    with pytest.raises(ValueError, match="metadata"):
        adapter.run(request)


def _runner() -> RunnerMetadata:
    return RunnerMetadata(
        id="runner_fixture",
        name="Fixture Runner",
        adapter="fixture",
        adapter_version="0.1.0",
        mode="fixture",
        capabilities=["prompt.read", "result.structured"],
        metadata={"contract_test": True},
    )


def _request(runner: RunnerMetadata) -> RunnerAdapterRequest:
    return RunnerAdapterRequest(
        id="runner_request_docs",
        task_id="task_docs_reconcile",
        runner=runner,
        task_request_id="task_docs_reconcile",
        case_file_id="case_docs_reconcile",
        policy_envelope_id="policy_docs_reconcile",
        capability_grant_ids=["grant_repo_read"],
        expected_output_schemas=["craik.runner_adapter_result", "craik.handoff"],
        context={"prompt": "Review docs against implementation state."},
        created_at=datetime(2026, 5, 16, 3, 30, tzinfo=UTC),
    )


def _result(
    runner: RunnerMetadata,
    *,
    status: RunnerResultStatus = "completed",
) -> RunnerAdapterResult:
    return RunnerAdapterResult(
        id=f"runner_result_{status}",
        request_id="runner_request_docs",
        task_id="task_docs_reconcile",
        runner=runner,
        status=status,
        summary="Fixture runner produced normalized output.",
        outputs={"handoff_summary": "Docs review completed."},
        receipt_ids=["receipt_runner_fixture"],
        handoff_id="handoff_docs_reconcile",
        memory_proposal_ids=["memprop_docs_reconcile"],
        artifacts=["case_docs_reconcile"],
        diagnostics=[],
        created_at=datetime(2026, 5, 16, 3, 31, tzinfo=UTC),
    )
