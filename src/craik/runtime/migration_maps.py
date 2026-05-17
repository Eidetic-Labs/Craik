"""Migration maps for memory, skill, and config imports."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel
from craik.runtime.migration_assessment import MigrationSupport

MigrationMapSurface = Literal["memory", "skill", "config"]


class MigrationFieldMap(CraikModel):
    """One source-to-target field mapping."""

    source_field: str
    target_field: str | None
    support: MigrationSupport
    transform_notes: str
    redaction_required: bool = True
    unsupported_reason: str | None = None

    @model_validator(mode="after")
    def validate_field_map(self) -> MigrationFieldMap:
        """Keep supported and unsupported fields explicit."""
        if self.support == "supported" and self.target_field is None:
            raise ValueError("supported migration fields require target_field")
        if self.support == "unsupported" and self.unsupported_reason is None:
            raise ValueError("unsupported migration fields require unsupported_reason")
        return self


class MigrationMap(CraikModel):
    """Migration map for one import surface."""

    id: str
    surface: MigrationMapSurface
    source_name: str
    field_maps: list[MigrationFieldMap] = Field(min_length=1)
    compatibility_notes: list[str] = Field(default_factory=list)
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_migration_map(self) -> MigrationMap:
        """Keep maps policy-bound."""
        if not self.policy_envelope_id:
            raise ValueError("migration maps require policy_envelope_id")
        return self
