"""Approval gates for promoted skill changes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel
from craik.runtime.skill_proposals import SkillChangeProposal

SkillPromotionDecisionStatus = Literal["approved", "denied"]


class SkillPromotionRequest(CraikModel):
    """Request to promote an approved skill proposal into reusable guidance."""

    id: str
    proposal_id: str
    skill_package_id: str
    promoted_version_id: str
    approver: str
    policy_envelope_id: str
    evidence_ids: list[str] = Field(default_factory=list)
    eval_result_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    approval_receipt_id: str | None = None
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_skill_promotion_request(self) -> SkillPromotionRequest:
        """Keep promotion requests bound to an explicit policy envelope."""
        if not self.policy_envelope_id:
            raise ValueError("skill promotion requests require policy_envelope_id")
        return self


class SkillPromotionDecision(CraikModel):
    """Auditable result of a skill promotion gate."""

    id: str
    request_id: str
    proposal_id: str
    skill_package_id: str
    status: SkillPromotionDecisionStatus
    approver: str | None = None
    promoted_version_id: str | None = None
    policy_envelope_id: str
    evidence_ids: list[str] = Field(default_factory=list)
    eval_result_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    denied_reasons: list[str] = Field(default_factory=list)
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_skill_promotion_decision(self) -> SkillPromotionDecision:
        """Keep approved and denied promotion decisions internally consistent."""
        if self.status == "approved":
            if self.approver is None:
                raise ValueError("approved skill promotions require approver")
            if self.promoted_version_id is None:
                raise ValueError("approved skill promotions require promoted_version_id")
            if self.denied_reasons:
                raise ValueError("approved skill promotions cannot include denied_reasons")
        if self.status == "denied" and not self.denied_reasons:
            raise ValueError("denied skill promotions require denied_reasons")
        return self


def decide_skill_promotion(
    *,
    decision_id: str,
    proposal: SkillChangeProposal,
    request: SkillPromotionRequest,
    decided_at: datetime | None = None,
) -> SkillPromotionDecision:
    """Approve promotion only after proposal, approval, eval, and receipt gates pass."""
    denied_reasons = _promotion_denied_reasons(proposal, request)
    now = decided_at or datetime.now(UTC)
    if denied_reasons:
        return SkillPromotionDecision(
            id=decision_id,
            request_id=request.id,
            proposal_id=request.proposal_id,
            skill_package_id=request.skill_package_id,
            status="denied",
            policy_envelope_id=request.policy_envelope_id,
            evidence_ids=list(request.evidence_ids),
            eval_result_ids=list(request.eval_result_ids),
            receipt_ids=list(request.receipt_ids),
            denied_reasons=denied_reasons,
            decided_at=now,
        )

    return SkillPromotionDecision(
        id=decision_id,
        request_id=request.id,
        proposal_id=request.proposal_id,
        skill_package_id=request.skill_package_id,
        status="approved",
        approver=request.approver,
        promoted_version_id=request.promoted_version_id,
        policy_envelope_id=request.policy_envelope_id,
        evidence_ids=list(request.evidence_ids),
        eval_result_ids=list(request.eval_result_ids),
        receipt_ids=list(request.receipt_ids),
        decided_at=now,
    )


def _promotion_denied_reasons(
    proposal: SkillChangeProposal,
    request: SkillPromotionRequest,
) -> list[str]:
    denied_reasons: list[str] = []
    if request.proposal_id != proposal.id:
        denied_reasons.append("promotion request proposal_id does not match proposal")
    if request.skill_package_id != proposal.skill_package_id:
        denied_reasons.append("promotion request skill_package_id does not match proposal")
    if request.policy_envelope_id != proposal.policy_envelope_id:
        denied_reasons.append("promotion policy_envelope_id does not match proposal")
    if proposal.status != "approved":
        denied_reasons.append("proposal must be approved before promotion")
    if proposal.improvement_plan is None:
        denied_reasons.append("promotion requires proposal improvement_plan")
    if not request.approver or request.approver.startswith("agent:"):
        denied_reasons.append("promotion requires explicit non-agent approver")
    if not request.evidence_ids:
        denied_reasons.append("promotion requires evidence_ids")
    if not request.eval_result_ids:
        denied_reasons.append("promotion requires eval_result_ids")
    if not request.receipt_ids:
        denied_reasons.append("promotion requires receipt_ids")
    if request.approval_receipt_id is None:
        denied_reasons.append("promotion requires approval_receipt_id")
    return denied_reasons
