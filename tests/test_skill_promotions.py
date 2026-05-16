from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.skill_promotions import (
    SkillPromotionDecision,
    SkillPromotionRequest,
    decide_skill_promotion,
)
from craik.runtime.skill_proposals import (
    SkillChangeProposal,
    SkillImprovementEdit,
    SkillImprovementPlan,
)

NOW = datetime(2026, 5, 16, 17, 10, tzinfo=UTC)


def _proposal(**overrides: object) -> SkillChangeProposal:
    payload = {
        "id": "skill_proposal_docs_reconcile",
        "skill_package_id": "skill_docs_reconcile",
        "task_id": "task_docs_reconcile",
        "title": "Clarify docs reconciliation validation",
        "summary": "Add explicit validation expectations to the skill.",
        "rationale": "Telemetry showed repeated missing validation output.",
        "proposed_change": "Require focused and full validation commands.",
        "source": "operator",
        "status": "approved",
        "policy_envelope_id": "policy_learning",
        "evidence_ids": ["evidence_skill_validation"],
        "receipt_ids": ["receipt_skill_proposal"],
        "improvement_plan": _improvement_plan(),
        "created_by": "user:maintainer",
        "created_at": NOW,
    }
    payload.update(overrides)
    return SkillChangeProposal.model_validate(payload)


def _request(**overrides: object) -> SkillPromotionRequest:
    payload = {
        "id": "skill_promotion_docs_reconcile",
        "proposal_id": "skill_proposal_docs_reconcile",
        "skill_package_id": "skill_docs_reconcile",
        "promoted_version_id": "skill_docs_reconcile@2026-05-16-promoted",
        "approver": "user:maintainer",
        "policy_envelope_id": "policy_learning",
        "evidence_ids": ["evidence_skill_validation"],
        "eval_result_ids": ["skill_replay_docs_fixture_result"],
        "receipt_ids": ["receipt_skill_proposal", "receipt_skill_promotion"],
        "approval_receipt_id": "receipt_skill_promotion",
        "requested_at": NOW,
    }
    payload.update(overrides)
    return SkillPromotionRequest.model_validate(payload)


def test_decide_skill_promotion_approves_when_all_gates_pass() -> None:
    decision = decide_skill_promotion(
        decision_id="skill_promotion_decision_docs_reconcile",
        proposal=_proposal(),
        request=_request(),
        decided_at=NOW,
    )

    assert decision.status == "approved"
    assert decision.approver == "user:maintainer"
    assert decision.promoted_version_id == "skill_docs_reconcile@2026-05-16-promoted"
    assert decision.policy_envelope_id == "policy_learning"
    assert decision.evidence_ids == ["evidence_skill_validation"]
    assert decision.eval_result_ids == ["skill_replay_docs_fixture_result"]
    assert decision.receipt_ids == ["receipt_skill_proposal", "receipt_skill_promotion"]
    assert decision.denied_reasons == []


def test_decide_skill_promotion_denies_pending_proposal() -> None:
    decision = decide_skill_promotion(
        decision_id="skill_promotion_decision_docs_reconcile",
        proposal=_proposal(status="pending_review", improvement_plan=None),
        request=_request(),
        decided_at=NOW,
    )

    assert decision.status == "denied"
    assert "proposal must be approved before promotion" in decision.denied_reasons
    assert "promotion requires proposal improvement_plan" in decision.denied_reasons


def test_decide_skill_promotion_denies_missing_required_gates() -> None:
    decision = decide_skill_promotion(
        decision_id="skill_promotion_decision_docs_reconcile",
        proposal=_proposal(),
        request=_request(
            approver="agent:codex",
            evidence_ids=[],
            eval_result_ids=[],
            receipt_ids=[],
            approval_receipt_id=None,
        ),
        decided_at=NOW,
    )

    assert decision.status == "denied"
    assert decision.promoted_version_id is None
    assert decision.denied_reasons == [
        "promotion requires explicit non-agent approver",
        "promotion requires evidence_ids",
        "promotion requires eval_result_ids",
        "promotion requires receipt_ids",
        "promotion requires approval_receipt_id",
    ]


def test_decide_skill_promotion_denies_mismatched_proposal_context() -> None:
    decision = decide_skill_promotion(
        decision_id="skill_promotion_decision_docs_reconcile",
        proposal=_proposal(),
        request=_request(
            proposal_id="skill_proposal_other",
            skill_package_id="skill_other",
            policy_envelope_id="policy_other",
        ),
        decided_at=NOW,
    )

    assert decision.status == "denied"
    assert "promotion request proposal_id does not match proposal" in decision.denied_reasons
    assert "promotion request skill_package_id does not match proposal" in decision.denied_reasons
    assert "promotion policy_envelope_id does not match proposal" in decision.denied_reasons


def test_skill_promotion_request_requires_policy() -> None:
    with pytest.raises(ValidationError, match="policy_envelope_id"):
        _request(policy_envelope_id="")


def test_skill_promotion_decision_validates_status_consistency() -> None:
    with pytest.raises(ValidationError, match="promoted_version_id"):
        SkillPromotionDecision(
            id="skill_promotion_decision_docs_reconcile",
            request_id="skill_promotion_docs_reconcile",
            proposal_id="skill_proposal_docs_reconcile",
            skill_package_id="skill_docs_reconcile",
            status="approved",
            approver="user:maintainer",
            policy_envelope_id="policy_learning",
            decided_at=NOW,
        )

    with pytest.raises(ValidationError, match="denied_reasons"):
        SkillPromotionDecision(
            id="skill_promotion_decision_docs_reconcile",
            request_id="skill_promotion_docs_reconcile",
            proposal_id="skill_proposal_docs_reconcile",
            skill_package_id="skill_docs_reconcile",
            status="denied",
            policy_envelope_id="policy_learning",
            decided_at=NOW,
        )


def _improvement_plan() -> SkillImprovementPlan:
    return SkillImprovementPlan(
        expected_benefit="Reduce missed validation steps.",
        risk="medium",
        rollback_notes="Use the prior stable version if replay regresses.",
        edits=[
            SkillImprovementEdit(
                target_ref="skill_docs_reconcile:checklist",
                change_summary="Add validation command requirements.",
                rationale="Telemetry showed missing validation output.",
            )
        ],
        replay_fixture_ids=["skill_replay_docs_fixture"],
    )
