"""Skill performance telemetry for learning loops."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel

SkillTelemetryOutcome = Literal["succeeded", "failed", "partial"]
SkillValidationStatus = Literal["passed", "failed", "skipped"]


class SkillValidationSignal(CraikModel):
    """One validation signal observed after a skill invocation."""

    name: str
    status: SkillValidationStatus
    summary: str
    evidence_ids: list[str] = Field(default_factory=list)


class SkillPerformanceTelemetry(CraikModel):
    """Redacted telemetry for one skill invocation."""

    id: str
    task_id: str
    skill_package_id: str
    skill_invocation_context_id: str
    outcome: SkillTelemetryOutcome
    duration_ms: int = Field(ge=0)
    validation_signals: list[SkillValidationSignal] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    policy_envelope_id: str | None = None
    redacted_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_skill_performance_telemetry(self) -> SkillPerformanceTelemetry:
        """Require auditable links and redacted metadata."""
        if not self.policy_envelope_id:
            raise ValueError("skill telemetry requires policy_envelope_id")
        if not self.receipt_ids:
            raise ValueError("skill telemetry requires receipt_ids")
        if self.outcome == "failed" and not any(
            signal.status == "failed" for signal in self.validation_signals
        ):
            raise ValueError("failed skill telemetry requires a failed validation signal")
        _reject_unredacted_metadata(self.redacted_metadata)
        return self


def skill_performance_telemetry(
    *,
    telemetry_id: str,
    task_id: str,
    skill_package_id: str,
    skill_invocation_context_id: str,
    outcome: SkillTelemetryOutcome,
    duration_ms: int,
    validation_signals: list[SkillValidationSignal],
    evidence_ids: list[str],
    receipt_ids: list[str],
    policy_envelope_id: str,
    metadata: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> SkillPerformanceTelemetry:
    """Build redacted skill telemetry from invocation results."""
    return SkillPerformanceTelemetry(
        id=telemetry_id,
        task_id=task_id,
        skill_package_id=skill_package_id,
        skill_invocation_context_id=skill_invocation_context_id,
        outcome=outcome,
        duration_ms=duration_ms,
        validation_signals=validation_signals,
        evidence_ids=evidence_ids,
        receipt_ids=receipt_ids,
        policy_envelope_id=policy_envelope_id,
        redacted_metadata=_redacted_metadata(metadata or {}),
        created_at=created_at or datetime.now(UTC),
    )


def _redacted_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in metadata.items():
        normalized = key.lower().replace("-", "_")
        if normalized in _REDACTED_METADATA_KEYS:
            continue
        if any(token in normalized for token in _SECRET_KEY_TOKENS):
            continue
        redacted[key] = value
    return redacted


def _reject_unredacted_metadata(metadata: dict[str, Any]) -> None:
    for key in metadata:
        normalized = key.lower().replace("-", "_")
        if normalized in _REDACTED_METADATA_KEYS or any(
            token in normalized for token in _SECRET_KEY_TOKENS
        ):
            raise ValueError("skill telemetry metadata must be redacted")


_REDACTED_METADATA_KEYS = {
    "input",
    "output",
    "payload",
    "prompt",
    "raw_error",
    "response",
    "stderr",
    "stdout",
    "trace",
}
_SECRET_KEY_TOKENS = ("secret", "token", "api_key", "apikey", "password", "credential")
