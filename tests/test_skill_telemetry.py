from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.skill_telemetry import (
    SkillPerformanceTelemetry,
    SkillValidationSignal,
    skill_performance_telemetry,
)

NOW = datetime(2026, 5, 16, 21, 0, tzinfo=UTC)


def _signal(status: str = "passed") -> SkillValidationSignal:
    return SkillValidationSignal(
        name="pytest",
        status=status,
        summary=f"Validation {status}.",
        evidence_ids=["evidence_skill_validation"],
    )


def test_skill_performance_telemetry_records_successful_invocation() -> None:
    telemetry = skill_performance_telemetry(
        telemetry_id="skill_telemetry_docs_success",
        task_id="task_docs_reconcile",
        skill_package_id="skill_docs_reconcile",
        skill_invocation_context_id="skill_context_docs_reconcile",
        outcome="succeeded",
        duration_ms=1250,
        validation_signals=[_signal()],
        evidence_ids=["evidence_skill_validation"],
        receipt_ids=["receipt_skill_validation"],
        policy_envelope_id="policy_docs_reconcile",
        metadata={"attempt": 1, "stdout": "raw output"},
        created_at=NOW,
    )

    assert telemetry.outcome == "succeeded"
    assert telemetry.duration_ms == 1250
    assert telemetry.validation_signals[0].status == "passed"
    assert telemetry.redacted_metadata == {"attempt": 1}
    assert telemetry.created_at == NOW


def test_skill_performance_telemetry_records_failed_invocation() -> None:
    telemetry = skill_performance_telemetry(
        telemetry_id="skill_telemetry_docs_failed",
        task_id="task_docs_reconcile",
        skill_package_id="skill_docs_reconcile",
        skill_invocation_context_id="skill_context_docs_reconcile",
        outcome="failed",
        duration_ms=700,
        validation_signals=[_signal("failed")],
        evidence_ids=["evidence_skill_validation"],
        receipt_ids=["receipt_skill_validation"],
        policy_envelope_id="policy_docs_reconcile",
        metadata={"error_kind": "missing_output", "raw_error": "secret traceback"},
        created_at=NOW,
    )

    assert telemetry.outcome == "failed"
    assert telemetry.validation_signals[0].status == "failed"
    assert telemetry.redacted_metadata == {"error_kind": "missing_output"}


def test_skill_performance_telemetry_requires_failed_signal_for_failed_outcome() -> None:
    with pytest.raises(ValidationError, match="failed validation signal"):
        skill_performance_telemetry(
            telemetry_id="skill_telemetry_docs_failed",
            task_id="task_docs_reconcile",
            skill_package_id="skill_docs_reconcile",
            skill_invocation_context_id="skill_context_docs_reconcile",
            outcome="failed",
            duration_ms=700,
            validation_signals=[_signal("passed")],
            evidence_ids=["evidence_skill_validation"],
            receipt_ids=["receipt_skill_validation"],
            policy_envelope_id="policy_docs_reconcile",
        )


def test_skill_performance_telemetry_requires_policy_and_receipts() -> None:
    with pytest.raises(ValidationError, match="policy_envelope_id"):
        skill_performance_telemetry(
            telemetry_id="skill_telemetry_docs_success",
            task_id="task_docs_reconcile",
            skill_package_id="skill_docs_reconcile",
            skill_invocation_context_id="skill_context_docs_reconcile",
            outcome="succeeded",
            duration_ms=1250,
            validation_signals=[_signal()],
            evidence_ids=["evidence_skill_validation"],
            receipt_ids=["receipt_skill_validation"],
            policy_envelope_id="",
        )

    with pytest.raises(ValidationError, match="receipt_ids"):
        skill_performance_telemetry(
            telemetry_id="skill_telemetry_docs_success",
            task_id="task_docs_reconcile",
            skill_package_id="skill_docs_reconcile",
            skill_invocation_context_id="skill_context_docs_reconcile",
            outcome="succeeded",
            duration_ms=1250,
            validation_signals=[_signal()],
            evidence_ids=["evidence_skill_validation"],
            receipt_ids=[],
            policy_envelope_id="policy_docs_reconcile",
        )


def test_skill_performance_telemetry_rejects_unredacted_metadata() -> None:
    with pytest.raises(ValidationError, match="metadata must be redacted"):
        SkillPerformanceTelemetry(
            id="skill_telemetry_docs_success",
            task_id="task_docs_reconcile",
            skill_package_id="skill_docs_reconcile",
            skill_invocation_context_id="skill_context_docs_reconcile",
            outcome="succeeded",
            duration_ms=1250,
            validation_signals=[_signal()],
            evidence_ids=["evidence_skill_validation"],
            receipt_ids=["receipt_skill_validation"],
            policy_envelope_id="policy_docs_reconcile",
            redacted_metadata={"api_token": "raw"},
        )
