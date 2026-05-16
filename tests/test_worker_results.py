import copy
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from craik.contracts.models import WorkerResult

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "contracts" / "v0_1" / "contracts.json"


@pytest.fixture(scope="module")
def fixtures() -> dict[str, dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text())


def test_worker_result_fixture_preserves_specialist_output(
    fixtures: dict[str, dict[str, Any]],
) -> None:
    result = WorkerResult.model_validate(fixtures["craik.worker_result"])

    assert result.role_kind == "verifier"
    assert result.runner is not None
    assert result.runner.id == "runner_fixture"
    assert result.findings[0].evidence_ids == ["evidence_readme_status"]
    assert result.receipt_ids == ["receipt_runner_fixture"]
    assert result.proposed_actions == ["Continue to adjudication."]


@pytest.mark.parametrize("status", ["completed", "blocked", "failed", "partial"])
def test_worker_result_accepts_all_worker_statuses(
    fixtures: dict[str, dict[str, Any]],
    status: str,
) -> None:
    payload = copy.deepcopy(fixtures["craik.worker_result"])
    payload["id"] = f"worker_result_docs_reconcile_{status}"
    payload["status"] = status

    result = WorkerResult.model_validate(payload)

    assert result.status == status


def test_worker_result_preserves_unresolved_contradictions(
    fixtures: dict[str, dict[str, Any]],
) -> None:
    payload = copy.deepcopy(fixtures["craik.worker_result"])
    payload["contradiction_ids"] = ["contradiction_docs_status"]
    payload["findings"][0]["contradiction_ids"] = ["contradiction_docs_status"]

    result = WorkerResult.model_validate(payload)

    assert result.contradiction_ids == ["contradiction_docs_status"]
    assert result.findings[0].contradiction_ids == ["contradiction_docs_status"]


def test_worker_result_rejects_unknown_status(fixtures: dict[str, dict[str, Any]]) -> None:
    payload = copy.deepcopy(fixtures["craik.worker_result"])
    payload["status"] = "merged"

    with pytest.raises(ValidationError):
        WorkerResult.model_validate(payload)
