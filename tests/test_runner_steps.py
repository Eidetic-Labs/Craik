import copy
import json
from pathlib import Path
from typing import Any

import pytest

from craik.contracts.models import RunnerStepRequest, RunnerStepResult

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "contracts" / "v0_1" / "contracts.json"


@pytest.fixture(scope="module")
def fixtures() -> dict[str, dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text())


def test_runner_step_request_preserves_policy_and_intent_boundaries(
    fixtures: dict[str, dict[str, Any]],
) -> None:
    request = RunnerStepRequest.model_validate(fixtures["craik.runner_step_request"])

    assert request.run_id == "run_docs_reconcile"
    assert request.phase == "plan"
    assert request.policy_envelope_id == "policy_docs_reconcile"
    assert request.intent_lock_id == "intent_docs_reconcile"
    assert request.capability_grant_ids == ["grant_repo_read"]
    assert request.redaction_required is True


@pytest.mark.parametrize(
    ("status", "diagnostics"),
    [
        ("completed", []),
        ("blocked", ["approval required before side effect"]),
        ("failed", ["runner exited non-zero"]),
        ("partial", ["runner returned incomplete observation"]),
    ],
)
def test_runner_step_result_accepts_all_runner_statuses(
    fixtures: dict[str, dict[str, Any]],
    status: str,
    diagnostics: list[str],
) -> None:
    payload = copy.deepcopy(fixtures["craik.runner_step_result"])
    payload["id"] = f"runner_step_result_docs_reconcile_{status}"
    payload["status"] = status
    payload["diagnostics"] = diagnostics

    result = RunnerStepResult.model_validate(payload)

    assert result.status == status
    assert result.diagnostics == diagnostics
    assert result.receipt_ids == ["receipt_runner_fixture"]
    assert result.memory_proposal_ids == ["memprop_docs_reconcile"]


def test_runner_step_result_preserves_redacted_runner_metadata(
    fixtures: dict[str, dict[str, Any]],
) -> None:
    result = RunnerStepResult.model_validate(fixtures["craik.runner_step_result"])

    assert result.redacted is True
    assert result.runner.metadata == {"contract_test": True}
    assert result.observed_output["runner_metadata"]["runner_specific"] == {
        "api_token": "[REDACTED]"
    }
