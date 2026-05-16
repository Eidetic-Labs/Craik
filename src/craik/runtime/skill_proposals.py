"""Autonomous skill proposal creation boundaries."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel

SkillProposalStatus = Literal["pending_review", "approved", "rejected"]
SkillProposalSource = Literal["telemetry", "operator", "review"]


class SkillChangeProposal(CraikModel):
    """Reviewable proposed change to reusable skill guidance."""

    id: str
    skill_package_id: str
    task_id: str
    title: str
    summary: str
    rationale: str
    proposed_change: str
    source: SkillProposalSource = "telemetry"
    status: SkillProposalStatus = "pending_review"
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    telemetry_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(min_length=1)
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_skill_change_proposal(self) -> SkillChangeProposal:
        """Keep autonomous proposals pending and evidence-backed."""
        if self.source == "telemetry" and not self.telemetry_ids:
            raise ValueError("telemetry-sourced skill proposals require telemetry_ids")
        if self.created_by.startswith("agent:") and self.status != "pending_review":
            raise ValueError("agent-created skill proposals must remain pending_review")
        if not self.policy_envelope_id:
            raise ValueError("skill proposals require policy_envelope_id")
        return self


def draft_skill_change_proposal(
    *,
    proposal_id: str,
    skill_package_id: str,
    task_id: str,
    title: str,
    summary: str,
    rationale: str,
    proposed_change: str,
    policy_envelope_id: str,
    evidence_ids: list[str],
    telemetry_ids: list[str],
    receipt_ids: list[str],
    created_by: str,
    created_at: datetime | None = None,
) -> SkillChangeProposal:
    """Create a pending skill change proposal from observed work."""
    return SkillChangeProposal(
        id=proposal_id,
        skill_package_id=skill_package_id,
        task_id=task_id,
        title=title,
        summary=summary,
        rationale=rationale,
        proposed_change=proposed_change,
        source="telemetry",
        status="pending_review",
        policy_envelope_id=policy_envelope_id,
        evidence_ids=evidence_ids,
        telemetry_ids=telemetry_ids,
        receipt_ids=receipt_ids,
        created_by=created_by,
        created_at=created_at or datetime.now(UTC),
    )
