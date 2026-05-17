"""Migration assessment records for adjacent tools."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel

MigrationSupport = Literal["supported", "partial", "unsupported"]
AdjacentToolConcept = Literal["project", "task", "memory", "skill", "config", "receipt"]


class AdjacentToolMapping(CraikModel):
    """One concept mapping from an adjacent tool to Craik."""

    source_concept: str
    target_concept: AdjacentToolConcept
    support: MigrationSupport
    notes: str
    required_controls: list[str] = Field(default_factory=list)
    unsupported_fields: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_mapping(self) -> AdjacentToolMapping:
        """Require unsupported details when a mapping is not complete."""
        if self.support in {"partial", "unsupported"} and not self.unsupported_fields:
            raise ValueError("partial or unsupported mappings require unsupported_fields")
        return self


class AdjacentToolMigrationAssessment(CraikModel):
    """Assessment of whether an adjacent tool can migrate into Craik."""

    id: str
    tool_name: str
    support: MigrationSupport
    mappings: list[AdjacentToolMapping] = Field(min_length=1)
    security_notes: list[str] = Field(default_factory=list)
    redaction_required: bool = True
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_assessment(self) -> AdjacentToolMigrationAssessment:
        """Keep assessment status consistent with mapping support."""
        if not self.policy_envelope_id:
            raise ValueError("migration assessments require policy_envelope_id")
        if any(mapping.support == "unsupported" for mapping in self.mappings):
            expected: MigrationSupport = "partial"
            if all(mapping.support == "unsupported" for mapping in self.mappings):
                expected = "unsupported"
            if self.support != expected:
                raise ValueError("assessment support must reflect unsupported mappings")
        if (
            all(mapping.support == "supported" for mapping in self.mappings)
            and self.support != "supported"
        ):
            raise ValueError("fully supported mappings require supported assessment")
        return self
