"""Import dry-run reports for migration workflows."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel

ImportRecordStatus = Literal["mapped", "warning", "error", "unsupported"]


class ImportCandidateRecord(CraikModel):
    """One source record considered during an import dry run."""

    source_id: str
    source_type: str
    summary: str
    redacted: bool = True


class ImportMappedRecord(CraikModel):
    """One mapped target record proposed by an import dry run."""

    source_id: str
    target_schema: str
    target_id: str
    status: ImportRecordStatus = "mapped"
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_mapped_record(self) -> ImportMappedRecord:
        """Require warning and error details for non-clean mappings."""
        if self.status == "warning" and not self.warnings:
            raise ValueError("warning import mappings require warnings")
        if self.status in {"error", "unsupported"} and not self.errors:
            raise ValueError("error or unsupported import mappings require errors")
        return self


class ImportDryRunReport(CraikModel):
    """Read-only report describing what an import would do."""

    id: str
    source_name: str
    source_kind: str
    candidates: list[ImportCandidateRecord] = Field(default_factory=list)
    mapped_records: list[ImportMappedRecord] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    mutated_state: Literal[False] = False
    redacted: bool = True
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_report(self) -> ImportDryRunReport:
        """Keep dry runs read-only and policy-bound."""
        if not self.policy_envelope_id:
            raise ValueError("import dry-run reports require policy_envelope_id")
        if any(record.status in {"error", "unsupported"} for record in self.mapped_records):
            if not self.errors:
                raise ValueError("dry-run reports with failed mappings require errors")
        return self


def import_dry_run_report(
    *,
    report_id: str,
    source_name: str,
    source_kind: str,
    candidates: list[ImportCandidateRecord],
    mapped_records: list[ImportMappedRecord],
    policy_envelope_id: str,
    evidence_ids: list[str],
    receipt_ids: list[str],
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    created_at: datetime | None = None,
) -> ImportDryRunReport:
    """Create a read-only import dry-run report."""
    return ImportDryRunReport(
        id=report_id,
        source_name=source_name,
        source_kind=source_kind,
        candidates=candidates,
        mapped_records=mapped_records,
        warnings=warnings or [],
        errors=errors or [],
        mutated_state=False,
        policy_envelope_id=policy_envelope_id,
        evidence_ids=evidence_ids,
        receipt_ids=receipt_ids,
        created_at=created_at or datetime.now(UTC),
    )
