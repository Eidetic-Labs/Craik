"""Reviewable rollback path for promoted skill updates."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel

SkillRollbackReason = Literal[
    "failed_replay",
    "behavior_regression",
    "policy_violation",
    "operator_request",
    "other",
]
SkillRollbackDecisionStatus = Literal["approved", "denied"]


class SkillRollbackTarget(CraikModel):
    """Skill versions involved in a rollback decision."""

    skill_package_id: str
    promoted_version_id: str
    rollback_version_id: str
    promoted_proposal_id: str | None = None
    promoted_receipt_id: str | None = None

    @model_validator(mode="after")
    def validate_skill_rollback_target(self) -> SkillRollbackTarget:
        """Ensure rollback targets a distinct prior version."""
        if self.promoted_version_id == self.rollback_version_id:
            raise ValueError("rollback_version_id must differ from promoted_version_id")
        return self


class SkillRollbackRequest(CraikModel):
    """Auditable request to roll back a promoted skill update."""

    id: str
    task_id: str
    target: SkillRollbackTarget
    reason: SkillRollbackReason
    rationale: str
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(min_length=1)
    replay_result_ids: list[str] = Field(default_factory=list)
    requested_by: str
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_skill_rollback_request(self) -> SkillRollbackRequest:
        """Keep rollback requests policy-bound and reviewable."""
        if not self.policy_envelope_id:
            raise ValueError("skill rollback requests require policy_envelope_id")
        return self


class SkillRollbackDecision(CraikModel):
    """Review result for a rollback request."""

    id: str
    request_id: str
    status: SkillRollbackDecisionStatus
    decided_by: str
    summary: str
    rollback_version_id: str | None = None
    decision_receipt_id: str | None = None
    denied_reasons: list[str] = Field(default_factory=list)
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_skill_rollback_decision(self) -> SkillRollbackDecision:
        """Keep approved and denied decisions internally consistent."""
        if self.status == "approved":
            if self.rollback_version_id is None:
                raise ValueError("approved rollback decisions require rollback_version_id")
            if self.decision_receipt_id is None:
                raise ValueError("approved rollback decisions require decision_receipt_id")
            if self.denied_reasons:
                raise ValueError("approved rollback decisions cannot include denied_reasons")
        if self.status == "denied" and not self.denied_reasons:
            raise ValueError("denied rollback decisions require denied_reasons")
        return self


def decide_skill_rollback(
    *,
    decision_id: str,
    request: SkillRollbackRequest,
    decided_by: str,
    decision_receipt_id: str | None,
    decided_at: datetime | None = None,
) -> SkillRollbackDecision:
    """Approve rollback only when review evidence and replay context are present."""
    denied_reasons = _rollback_denied_reasons(request, decision_receipt_id)
    if denied_reasons:
        return SkillRollbackDecision(
            id=decision_id,
            request_id=request.id,
            status="denied",
            decided_by=decided_by,
            summary="Skill rollback denied.",
            denied_reasons=denied_reasons,
            decided_at=decided_at or datetime.now(UTC),
        )

    return SkillRollbackDecision(
        id=decision_id,
        request_id=request.id,
        status="approved",
        decided_by=decided_by,
        summary="Skill rollback approved.",
        rollback_version_id=request.target.rollback_version_id,
        decision_receipt_id=decision_receipt_id,
        decided_at=decided_at or datetime.now(UTC),
    )


def _rollback_denied_reasons(
    request: SkillRollbackRequest,
    decision_receipt_id: str | None,
) -> list[str]:
    denied_reasons: list[str] = []
    if not request.replay_result_ids:
        denied_reasons.append("rollback requires replay_result_ids")
    if decision_receipt_id is None:
        denied_reasons.append("rollback requires decision_receipt_id")
    return denied_reasons
