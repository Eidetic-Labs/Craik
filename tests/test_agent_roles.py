import copy
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from craik.contracts.models import AgentRole

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "contracts" / "v0_1" / "contracts.json"


@pytest.fixture(scope="module")
def fixtures() -> dict[str, dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text())


def test_agent_role_fixture_defines_policy_aware_orchestrator(
    fixtures: dict[str, dict[str, Any]],
) -> None:
    role = AgentRole.model_validate(fixtures["craik.agent_role"])

    assert role.kind == "orchestrator"
    assert "coordinate" in role.authority
    assert role.policy_envelope_id == "policy_docs_reconcile"
    assert role.runner_id == "runner_fixture"
    assert role.expected_input_schemas == ["craik.case_file", "craik.task_request"]
    assert "craik.handoff" in role.expected_output_schemas
    assert role.handoff_required is True
    assert role.receipt_required is True
    assert role.redaction_required is True


@pytest.mark.parametrize(
    ("kind", "authority"),
    [
        ("implementer", ["implement"]),
        ("verifier", ["review"]),
        ("policy_reviewer", ["review"]),
        ("memory_curator", ["review"]),
        ("adjudicator", ["adjudicate"]),
    ],
)
def test_specialist_roles_validate(kind: str, authority: list[str]) -> None:
    role = AgentRole.model_validate(
        {
            "schema": "craik.agent_role",
            "version": "0.1.0",
            "id": f"role_{kind}",
            "kind": kind,
            "name": kind.replace("_", " ").title(),
            "description": "Fixture specialist role.",
            "runner_id": "runner_fixture",
            "runner_mode": "fixture",
            "authority": authority,
            "allowed_capabilities": ["memory.read", "receipt.write"],
            "denied_capabilities": ["memory.write"],
            "expected_input_schemas": ["craik.case_file"],
            "expected_output_schemas": ["craik.worker_result"],
        }
    )

    assert role.kind == kind
    assert role.authority == authority
    assert role.expected_output_schemas == ["craik.worker_result"]


def test_invalid_role_authority_is_rejected(fixtures: dict[str, dict[str, Any]]) -> None:
    payload = copy.deepcopy(fixtures["craik.agent_role"])
    payload["authority"] = ["implement"]

    with pytest.raises(ValidationError, match="orchestrator role requires"):
        AgentRole.model_validate(payload)


def test_missing_expected_outputs_are_rejected(fixtures: dict[str, dict[str, Any]]) -> None:
    payload = copy.deepcopy(fixtures["craik.agent_role"])
    payload["expected_output_schemas"] = []

    with pytest.raises(ValidationError, match="expected output schema"):
        AgentRole.model_validate(payload)
