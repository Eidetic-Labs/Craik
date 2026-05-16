"""Training trajectory export format for replay and review."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field

from craik.contracts.models import (
    CapabilityReceipt,
    CraikModel,
    EvidenceReference,
    RunnerResultStatus,
    RunnerStepResult,
    TaskRunPhase,
)
from craik.runtime.redaction import REDACTION, redact

TRAJECTORY_EXPORT_FORMAT: Literal["craik.training_trajectory.v1"] = (
    "craik.training_trajectory.v1"
)
LOCAL_PATH_REDACTION = "[LOCAL_PATH]"

_PRIVATE_PAYLOAD_KEYS = {
    "conversation",
    "credentials",
    "payload",
    "private_payload",
    "prompt",
    "raw_output",
    "raw_trajectory",
    "request",
    "response",
    "trace",
    "trajectory",
}
_LOCAL_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?<![\w.-])/(?:Users|private|tmp|var/folders)/[^\s'\"),\]}]+"),
    re.compile(r"(?i)\b[A-Z]:\\Users\\[^\s'\"),\]}]+"),
)


class TrainingTrajectoryDecision(CraikModel):
    """One redacted decision or observation in an exported trajectory."""

    id: str
    step_result_id: str
    phase: TaskRunPhase
    runner_id: str
    status: RunnerResultStatus
    summary: str
    observed_output: dict[str, Any] = Field(default_factory=dict)
    diagnostics: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    created_at: datetime


class TrainingTrajectoryExport(CraikModel):
    """Stable, redacted training trajectory export envelope."""

    schema_: Literal["craik.training_trajectory_export"] = Field(
        default="craik.training_trajectory_export",
        alias="schema",
    )
    version: Literal["0.1.0"] = "0.1.0"
    format_version: Literal["craik.training_trajectory.v1"] = TRAJECTORY_EXPORT_FORMAT
    id: str
    task_id: str
    outcome: str
    decisions: list[TrainingTrajectoryDecision] = Field(min_length=1)
    receipts: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    compatibility_notes: list[str] = Field(default_factory=list)
    redacted_paths: list[str] = Field(default_factory=list)
    redacted: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def build_training_trajectory_export(
    *,
    export_id: str,
    task_id: str,
    steps: list[RunnerStepResult],
    outcome: str,
    receipts: list[CapabilityReceipt] | None = None,
    evidence: list[EvidenceReference] | None = None,
    compatibility_notes: list[str] | None = None,
    created_at: datetime | None = None,
) -> TrainingTrajectoryExport:
    """Build a redacted trajectory export from runner steps and review records."""
    redacted_paths: list[str] = []
    evidence_by_id = {item.id: item for item in evidence or []}
    decisions = [
        _decision_from_step(step, evidence_by_id=evidence_by_id, redacted_paths=redacted_paths)
        for step in steps
    ]
    safe_receipts = [
        _safe_payload(receipt.model_dump(by_alias=True, mode="json"), redacted_paths)
        for receipt in receipts or []
    ]
    safe_evidence = [
        _safe_payload(item.model_dump(by_alias=True, mode="json"), redacted_paths)
        for item in evidence or []
    ]

    return TrainingTrajectoryExport(
        id=export_id,
        task_id=task_id,
        outcome=str(_safe_payload(outcome, redacted_paths)),
        decisions=decisions,
        receipts=[item for item in safe_receipts if isinstance(item, dict)],
        evidence=[item for item in safe_evidence if isinstance(item, dict)],
        receipt_ids=sorted({receipt.id for receipt in receipts or []} | _step_receipt_ids(steps)),
        evidence_ids=sorted(evidence_by_id),
        compatibility_notes=compatibility_notes
        or ["Consumers must ignore unknown fields and preserve format_version."],
        redacted_paths=sorted(set(redacted_paths)),
        created_at=created_at or datetime.now(UTC),
    )


def _decision_from_step(
    step: RunnerStepResult,
    *,
    evidence_by_id: dict[str, EvidenceReference],
    redacted_paths: list[str],
) -> TrainingTrajectoryDecision:
    evidence_ids = _string_ids(step.observed_output.get("evidence_ids"))
    return TrainingTrajectoryDecision(
        id=f"trajectory_decision_{step.id}",
        step_result_id=step.id,
        phase=step.phase,
        runner_id=step.runner.id,
        status=step.status,
        summary=str(_safe_payload(step.summary, redacted_paths)),
        observed_output=_safe_dict(step.observed_output, redacted_paths),
        diagnostics=[str(_safe_payload(item, redacted_paths)) for item in step.diagnostics],
        artifacts=[str(_safe_payload(item, redacted_paths)) for item in step.artifacts],
        receipt_ids=list(step.receipt_ids),
        evidence_ids=[item for item in evidence_ids if item in evidence_by_id],
        created_at=step.created_at,
    )


def _safe_payload(value: Any, redacted_paths: list[str]) -> Any:
    redacted = redact(value)
    redacted_paths.extend(redacted.redacted_paths)
    return _redact_private_payloads(redacted.value, "$", redacted_paths)


def _redact_private_payloads(value: Any, path: str, redacted_paths: list[str]) -> Any:
    if isinstance(value, str):
        return _redact_local_paths(value, path, redacted_paths)
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            child_path = f"{path}.{key}"
            normalized = str(key).lower().replace("-", "_")
            if normalized in _PRIVATE_PAYLOAD_KEYS:
                safe[key] = REDACTION
                redacted_paths.append(child_path)
            else:
                safe[key] = _redact_private_payloads(item, child_path, redacted_paths)
        return safe
    if isinstance(value, list):
        return [
            _redact_private_payloads(item, f"{path}[{index}]", redacted_paths)
            for index, item in enumerate(value)
        ]
    return value


def _redact_local_paths(value: str, path: str, redacted_paths: list[str]) -> str:
    redacted = value
    for pattern in _LOCAL_PATH_PATTERNS:
        redacted = pattern.sub(LOCAL_PATH_REDACTION, redacted)
    if redacted != value:
        redacted_paths.append(path)
    return redacted


def _safe_dict(value: dict[str, Any], redacted_paths: list[str]) -> dict[str, Any]:
    safe = _safe_payload(value, redacted_paths)
    if isinstance(safe, dict):
        return safe
    return {}


def _string_ids(value: Any) -> list[str]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    return []


def _step_receipt_ids(steps: list[RunnerStepResult]) -> set[str]:
    return {receipt_id for step in steps for receipt_id in step.receipt_ids}
