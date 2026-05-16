from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.skill_proposals import (
    SkillChangeProposal,
    SkillImprovementEdit,
    SkillImprovementPlan,
    draft_skill_change_proposal,
)

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
        improvement_plan=_improvement_plan(),
        created_by="user:maintainer",
        created_at=NOW,
    )

    assert proposal.status == "approved"


def test_skill_improvement_plan_records_benefit_risk_edits_and_rollback() -> None:
    proposal = _proposal(improvement_plan=_improvement_plan())

    assert proposal.improvement_plan is not None
    assert proposal.improvement_plan.expected_benefit == "Reduce missed validation steps."
    assert proposal.improvement_plan.risk == "medium"
    assert proposal.improvement_plan.rollback_notes == "Revert checklist wording if replay fails."
    assert proposal.improvement_plan.edits[0].target_ref == "skill_docs_reconcile:checklist"


def test_high_risk_skill_improvements_require_replay_fixtures() -> None:
    with pytest.raises(ValidationError, match="replay_fixture_ids"):
        _improvement_plan(risk="high", replay_fixture_ids=[])


def test_approved_skill_proposals_require_improvement_plan() -> None:
    with pytest.raises(ValidationError, match="improvement_plan"):
        SkillChangeProposal(
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


def _improvement_plan(**overrides: object) -> SkillImprovementPlan:
    payload = {
        "expected_benefit": "Reduce missed validation steps.",
        "risk": "medium",
        "rollback_notes": "Revert checklist wording if replay fails.",
        "edits": [
            SkillImprovementEdit(
                target_ref="skill_docs_reconcile:checklist",
                change_summary="Add validation command requirements.",
                rationale="Telemetry showed missing validation output.",
            )
        ],
        "replay_fixture_ids": ["skill_replay_docs_fixture"],
    }
    payload.update(overrides)
    return SkillImprovementPlan.model_validate(payload)
