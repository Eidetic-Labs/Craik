"""Learning-loop capability receipt builders."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field

from craik.contracts.models import CapabilityReceipt, CraikModel, PolicyProfile, ReceiptResult

LearningReceiptAction = Literal[
    "proposal",
    "review",
    "eval_replay",
    "promotion",
    "rollback",
    "export",
]


class LearningReceiptContext(CraikModel):
    """Context links preserved in learning-loop receipts."""

    task_id: str
    policy_envelope_id: str | None = None
    skill_package_id: str | None = None
    proposal_id: str | None = None
    telemetry_id: str | None = None
    replay_fixture_id: str | None = None
    preference_id: str | None = None
    memory_fact_ref: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)


def learning_receipt(
    *,
    receipt_id: str,
    action: LearningReceiptAction,
    context: LearningReceiptContext,
    actor: str,
    capability: str,
    policy_profile: PolicyProfile,
    status: Literal["passed", "denied"],
    reason: str,
    summary: str,
    metadata: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> CapabilityReceipt:
    """Build a redacted receipt for learning-loop decisions."""
    now = created_at or datetime.now(UTC)
    return CapabilityReceipt(
        id=receipt_id,
        task_id=context.task_id,
        actor=actor,
        capability=capability,
        target=_target(action, context),
        policy_profile=policy_profile,
        fail_open=False,
        reason=reason,
        result=ReceiptResult(
            status=status,
            summary=summary,
            metadata={
                **_context_metadata(context),
                "learning_action": action,
                **_redacted_metadata(metadata or {}),
                "redacted_fields": sorted(_REDACTED_METADATA_KEYS),
            },
        ),
        redacted=True,
        created_at=now,
    )


def _target(action: LearningReceiptAction, context: LearningReceiptContext) -> str:
    for value in (
        context.proposal_id,
        context.replay_fixture_id,
        context.preference_id,
        context.skill_package_id,
        context.memory_fact_ref,
    ):
        if value:
            return f"{action}:{value}"
    return action


def _context_metadata(context: LearningReceiptContext) -> dict[str, Any]:
    return {
        "policy_envelope_id": context.policy_envelope_id,
        "skill_package_id": context.skill_package_id,
        "proposal_id": context.proposal_id,
        "telemetry_id": context.telemetry_id,
        "replay_fixture_id": context.replay_fixture_id,
        "preference_id": context.preference_id,
        "memory_fact_ref": context.memory_fact_ref,
        "evidence_ids": context.evidence_ids,
        "receipt_ids": context.receipt_ids,
    }


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


_REDACTED_METADATA_KEYS = {
    "conversation",
    "credentials",
    "export_payload",
    "payload",
    "preference_evidence",
    "prompt",
    "raw_trajectory",
    "response",
    "trace",
    "trajectory",
}
_SECRET_KEY_TOKENS = ("secret", "token", "api_key", "apikey", "password", "credential")
