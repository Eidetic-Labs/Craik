from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.skill_proposals import SkillChangeProposal, draft_skill_change_proposal

NOW = datetime(2026, 5, 16, 21, 5, tzinfo=UTC)


def _proposal(**overrides: object) -> SkillChangeProposal:
    payload = {
        "proposal_id": "skill_proposal_docs_reconcile",
        "skill_package_id": "skill_docs_reconcile",
        "task_id": "task_docs_reconcile",
        "title": "Clarify docs reconciliation validation",
        "summary": "Add explicit validation expectations to the skill.",
        "rationale": "Telemetry showed repeated missing validation output.",
        "proposed_change": "Require focused and full validation commands in the skill checklist.",
        "policy_envelope_id": "policy_docs_reconcile",
        "evidence_ids": ["evidence_skill_validation"],
        "telemetry_ids": ["skill_telemetry_docs_failed"],
        "receipt_ids": ["receipt_skill_proposal"],
        "created_by": "agent:codex",
        "created_at": NOW,
    }
    payload.update(overrides)
    return draft_skill_change_proposal(**payload)


def test_draft_skill_change_proposal_creates_pending_review_record() -> None:
    proposal = _proposal()

    assert proposal.status == "pending_review"
    assert proposal.source == "telemetry"
    assert proposal.created_by == "agent:codex"
    assert proposal.telemetry_ids == ["skill_telemetry_docs_failed"]
    assert proposal.created_at == NOW


def test_skill_change_proposal_requires_evidence_receipts_and_policy() -> None:
    with pytest.raises(ValidationError):
        _proposal(evidence_ids=[])

    with pytest.raises(ValidationError):
        _proposal(receipt_ids=[])

    with pytest.raises(ValidationError, match="policy_envelope_id"):
        _proposal(policy_envelope_id="")


def test_telemetry_sourced_skill_proposal_requires_telemetry() -> None:
    with pytest.raises(ValidationError, match="telemetry_ids"):
        _proposal(telemetry_ids=[])


def test_agent_created_skill_proposal_cannot_skip_review() -> None:
    with pytest.raises(ValidationError, match="pending_review"):
        SkillChangeProposal(
            id="skill_proposal_promoted",
            skill_package_id="skill_docs_reconcile",
            task_id="task_docs_reconcile",
            title="Unsafe auto approval",
            summary="Attempt to skip review.",
            rationale="Not allowed.",
            proposed_change="Promote immediately.",
            source="operator",
            status="approved",
            policy_envelope_id="policy_docs_reconcile",
            evidence_ids=["evidence_skill_validation"],
            receipt_ids=["receipt_skill_proposal"],
            created_by="agent:codex",
            created_at=NOW,
        )


def test_non_agent_proposal_status_can_reflect_review_result() -> None:
    proposal = SkillChangeProposal(
        id="skill_proposal_reviewed",
        skill_package_id="skill_docs_reconcile",
        task_id="task_docs_reconcile",
        title="Reviewed change",
        summary="Human-reviewed proposal.",
        rationale="Operator approved it.",
        proposed_change="Update checklist.",
        source="operator",
        status="approved",
        policy_envelope_id="policy_docs_reconcile",
        evidence_ids=["evidence_skill_validation"],
        receipt_ids=["receipt_skill_proposal"],
        created_by="user:maintainer",
        created_at=NOW,
    )

    assert proposal.status == "approved"
