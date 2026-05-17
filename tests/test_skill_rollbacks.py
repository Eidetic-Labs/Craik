from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.skills.skill_rollbacks import (
    SkillRollbackDecision,
    SkillRollbackRequest,
    SkillRollbackTarget,
    decide_skill_rollback,
)

NOW = datetime(2026, 5, 16, 16, 35, tzinfo=UTC)


def _target(**overrides: object) -> SkillRollbackTarget:
    payload = {
        "skill_package_id": "skill_docs_reconcile",
        "promoted_version_id": "skill_docs_reconcile@2026-05-16-promoted",
        "rollback_version_id": "skill_docs_reconcile@2026-05-15-stable",
        "promoted_proposal_id": "skill_proposal_docs_reconcile",
        "promoted_receipt_id": "receipt_skill_promotion",
    }
    payload.update(overrides)
    return SkillRollbackTarget.model_validate(payload)


def _request(**overrides: object) -> SkillRollbackRequest:
    payload = {
        "id": "skill_rollback_docs_reconcile",
        "task_id": "task_docs_reconcile",
        "target": _target(),
        "reason": "failed_replay",
        "rationale": "Promotion caused fixture replay regressions.",
        "policy_envelope_id": "policy_learning",
        "evidence_ids": ["evidence_replay_regression"],
        "receipt_ids": ["receipt_learning_rollback"],
        "replay_result_ids": ["skill_replay_docs_fixture_result"],
        "requested_by": "user:maintainer",
        "requested_at": NOW,
    }
    payload.update(overrides)
    return SkillRollbackRequest.model_validate(payload)


def test_decide_skill_rollback_approves_eligible_request() -> None:
    decision = decide_skill_rollback(
        decision_id="skill_rollback_decision_docs_reconcile",
        request=_request(),
        decided_by="user:maintainer",
        decision_receipt_id="receipt_skill_rollback_decision",
        decided_at=NOW,
    )

    assert decision.status == "approved"
    assert decision.rollback_version_id == "skill_docs_reconcile@2026-05-15-stable"
    assert decision.decision_receipt_id == "receipt_skill_rollback_decision"
    assert decision.denied_reasons == []
    assert decision.decided_at == NOW


def test_decide_skill_rollback_denies_without_replay_context() -> None:
    decision = decide_skill_rollback(
        decision_id="skill_rollback_decision_docs_reconcile",
        request=_request(replay_result_ids=[]),
        decided_by="user:maintainer",
        decision_receipt_id="receipt_skill_rollback_decision",
        decided_at=NOW,
    )

    assert decision.status == "denied"
    assert decision.rollback_version_id is None
    assert decision.decision_receipt_id is None
    assert decision.denied_reasons == ["rollback requires replay_result_ids"]


def test_decide_skill_rollback_denies_without_decision_receipt() -> None:
    decision = decide_skill_rollback(
        decision_id="skill_rollback_decision_docs_reconcile",
        request=_request(),
        decided_by="user:maintainer",
        decision_receipt_id=None,
        decided_at=NOW,
    )

    assert decision.status == "denied"
    assert decision.denied_reasons == ["rollback requires decision_receipt_id"]


def test_skill_rollback_request_requires_policy_evidence_and_receipts() -> None:
    with pytest.raises(ValidationError, match="policy_envelope_id"):
        _request(policy_envelope_id="")

    with pytest.raises(ValidationError):
        _request(evidence_ids=[])

    with pytest.raises(ValidationError):
        _request(receipt_ids=[])


def test_skill_rollback_target_requires_prior_version() -> None:
    with pytest.raises(ValidationError, match="rollback_version_id"):
        _target(rollback_version_id="skill_docs_reconcile@2026-05-16-promoted")


def test_skill_rollback_decision_validates_status_consistency() -> None:
    with pytest.raises(ValidationError, match="decision_receipt_id"):
        SkillRollbackDecision(
            id="skill_rollback_decision_docs_reconcile",
            request_id="skill_rollback_docs_reconcile",
            status="approved",
            decided_by="user:maintainer",
            summary="Approved.",
            rollback_version_id="skill_docs_reconcile@2026-05-15-stable",
            decided_at=NOW,
        )

    with pytest.raises(ValidationError, match="denied_reasons"):
        SkillRollbackDecision(
            id="skill_rollback_decision_docs_reconcile",
            request_id="skill_rollback_docs_reconcile",
            status="denied",
            decided_by="user:maintainer",
            summary="Denied.",
            decided_at=NOW,
        )
