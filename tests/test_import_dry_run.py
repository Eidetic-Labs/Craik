from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.import_dry_run import (
    ImportCandidateRecord,
    ImportDryRunReport,
    ImportMappedRecord,
    import_dry_run_report,
)

NOW = datetime(2026, 5, 16, 20, 10, tzinfo=UTC)


def test_import_dry_run_report_records_candidates_and_mappings_without_mutation() -> None:
    report = import_dry_run_report(
        report_id="import_dry_run_editor_tasks",
        source_name="Editor Task Tool",
        source_kind="adjacent_tool",
        candidates=[_candidate()],
        mapped_records=[_mapped_record()],
        policy_envelope_id="policy_migration",
        evidence_ids=["evidence_import_source"],
        receipt_ids=["receipt_import_dry_run"],
        created_at=NOW,
    )

    assert report.mutated_state is False
    assert report.redacted is True
    assert report.candidates[0].source_id == "source_task_1"
    assert report.mapped_records[0].target_schema == "craik.task_request"
    assert report.policy_envelope_id == "policy_migration"
    assert report.created_at == NOW


def test_import_dry_run_report_preserves_warnings_and_errors() -> None:
    report = import_dry_run_report(
        report_id="import_dry_run_editor_tasks",
        source_name="Editor Task Tool",
        source_kind="adjacent_tool",
        candidates=[_candidate()],
        mapped_records=[
            _mapped_record(status="unsupported", errors=["secret fields cannot be imported"])
        ],
        warnings=["one record needs operator review"],
        errors=["unsupported records present"],
        policy_envelope_id="policy_migration",
        evidence_ids=["evidence_import_source"],
        receipt_ids=["receipt_import_dry_run"],
        created_at=NOW,
    )

    assert report.warnings == ["one record needs operator review"]
    assert report.errors == ["unsupported records present"]
    assert report.mapped_records[0].status == "unsupported"


def test_import_mapped_record_requires_details_for_non_clean_status() -> None:
    with pytest.raises(ValidationError, match="warnings"):
        _mapped_record(status="warning")

    with pytest.raises(ValidationError, match="errors"):
        _mapped_record(status="error")


def test_import_dry_run_report_requires_policy_evidence_and_receipts() -> None:
    with pytest.raises(ValidationError, match="policy_envelope_id"):
        import_dry_run_report(
            report_id="import_dry_run_editor_tasks",
            source_name="Editor Task Tool",
            source_kind="adjacent_tool",
            candidates=[_candidate()],
            mapped_records=[_mapped_record()],
            policy_envelope_id="",
            evidence_ids=["evidence_import_source"],
            receipt_ids=["receipt_import_dry_run"],
        )

    with pytest.raises(ValidationError):
        import_dry_run_report(
            report_id="import_dry_run_editor_tasks",
            source_name="Editor Task Tool",
            source_kind="adjacent_tool",
            candidates=[_candidate()],
            mapped_records=[_mapped_record()],
            policy_envelope_id="policy_migration",
            evidence_ids=[],
            receipt_ids=["receipt_import_dry_run"],
        )


def test_import_dry_run_report_requires_summary_errors_for_failed_mappings() -> None:
    with pytest.raises(ValidationError, match="failed mappings"):
        ImportDryRunReport(
            id="import_dry_run_editor_tasks",
            source_name="Editor Task Tool",
            source_kind="adjacent_tool",
            candidates=[_candidate()],
            mapped_records=[
                _mapped_record(status="unsupported", errors=["secret fields cannot be imported"])
            ],
            policy_envelope_id="policy_migration",
            evidence_ids=["evidence_import_source"],
            receipt_ids=["receipt_import_dry_run"],
            created_at=NOW,
        )


def _candidate() -> ImportCandidateRecord:
    return ImportCandidateRecord(
        source_id="source_task_1",
        source_type="task",
        summary="Create migrated task.",
    )


def _mapped_record(**overrides: object) -> ImportMappedRecord:
    payload = {
        "source_id": "source_task_1",
        "target_schema": "craik.task_request",
        "target_id": "task_imported_1",
        "status": "mapped",
    }
    payload.update(overrides)
    return ImportMappedRecord.model_validate(payload)
