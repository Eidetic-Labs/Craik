"""Reviewable user and team preference facts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel

PreferenceScope = Literal["user", "team"]
PreferenceStatus = Literal["inferred", "approved", "rejected"]


class PreferenceFact(CraikModel):
    """Reviewable preference fact candidate."""

    id: str
    subject: str
    scope: PreferenceScope
    statement: str
    status: PreferenceStatus = "inferred"
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(min_length=1)
    inferred_from: list[str] = Field(default_factory=list)
    reviewed_by: str | None = None
    review_reason: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_preference_fact(self) -> PreferenceFact:
        """Keep inferred preferences separate from reviewed facts."""
        if self.scope == "user" and not self.subject.startswith("user:"):
            raise ValueError("user preference facts require user subject")
        if self.scope == "team" and not self.subject.startswith("team:"):
            raise ValueError("team preference facts require team subject")
        reviewed_fields = (self.reviewed_by, self.review_reason, self.reviewed_at)
        if self.status == "inferred":
            if any(value is not None for value in reviewed_fields):
                raise ValueError("inferred preference facts must not include review fields")
            if not self.inferred_from:
                raise ValueError("inferred preference facts require inferred_from")
        if self.status in {"approved", "rejected"}:
            if not all(reviewed_fields):
                raise ValueError("reviewed preference facts require review fields")
        return self


def review_preference_fact(
    preference: PreferenceFact,
    *,
    status: Literal["approved", "rejected"],
    reviewed_by: str,
    review_reason: str,
    reviewed_at: datetime | None = None,
) -> PreferenceFact:
    """Return a reviewed preference without changing the original record."""
    return PreferenceFact(
        **{
            **preference.model_dump(),
            "status": status,
            "reviewed_by": reviewed_by,
            "review_reason": review_reason,
            "reviewed_at": reviewed_at or datetime.now(UTC),
        }
    )
