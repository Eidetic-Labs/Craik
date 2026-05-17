"""Periodic memory review nudges for learning loops."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel, MemoryScope

MemoryReviewReason = Literal["stale", "expiring", "low_confidence", "missing_evidence"]
MemoryReviewStatus = Literal["due", "not_due"]


class MemoryReviewCandidate(CraikModel):
    """Memory fact candidate considered for review."""

    fact_ref: str
    entity: str
    relation: str
    scope: MemoryScope
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)
    last_reviewed_at: datetime | None = None
    expires_at: datetime | None = None
    owner: str | None = None


class MemoryReviewNudge(CraikModel):
    """Review nudge that does not rewrite memory facts."""

    id: str
    candidate_ref: str
    status: MemoryReviewStatus
    reasons: list[MemoryReviewReason] = Field(default_factory=list)
    owner: str | None = None
    due_at: datetime | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_memory_review_nudge(self) -> MemoryReviewNudge:
        """Require audit links for due review nudges."""
        if self.status == "due":
            if not self.reasons:
                raise ValueError("due memory review nudges require reasons")
            if not self.receipt_ids:
                raise ValueError("due memory review nudges require receipt_ids")
        if self.status == "not_due" and self.reasons:
            raise ValueError("not_due memory review nudges must not include reasons")
        return self


def memory_review_nudge(
    *,
    nudge_id: str,
    candidate: MemoryReviewCandidate,
    now: datetime,
    review_interval_days: int,
    min_confidence: float = 0.5,
    receipt_ids: list[str] | None = None,
) -> MemoryReviewNudge:
    """Create a review nudge when a memory candidate needs review."""
    reasons: list[MemoryReviewReason] = []
    if candidate.last_reviewed_at is None or (
        now - candidate.last_reviewed_at
    ).days >= review_interval_days:
        reasons.append("stale")
    if candidate.expires_at is not None and candidate.expires_at <= now:
        reasons.append("expiring")
    if candidate.confidence < min_confidence:
        reasons.append("low_confidence")
    if not candidate.evidence_ids:
        reasons.append("missing_evidence")
    if not reasons:
        return MemoryReviewNudge(
            id=nudge_id,
            candidate_ref=candidate.fact_ref,
            status="not_due",
            owner=candidate.owner,
            evidence_ids=candidate.evidence_ids,
            created_at=now,
        )
    return MemoryReviewNudge(
        id=nudge_id,
        candidate_ref=candidate.fact_ref,
        status="due",
        reasons=sorted(set(reasons)),
        owner=candidate.owner,
        due_at=now,
        evidence_ids=candidate.evidence_ids,
        receipt_ids=receipt_ids or [],
        created_at=now,
    )
