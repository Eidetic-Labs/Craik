"""Gateway receipt builders for always-on service actions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field

from craik.contracts.models import CapabilityReceipt, CraikModel, PolicyProfile, ReceiptResult

GatewayReceiptAction = Literal[
    "inbound_event",
    "dispatch_decision",
    "policy_check",
    "denial",
    "scheduled_automation",
]


class GatewayReceiptContext(CraikModel):
    """Context links preserved in gateway receipts."""

    channel: str | None = None
    event_id: str | None = None
    task_id: str
    policy_envelope_id: str | None = None
    identity_id: str | None = None
    subject: str | None = None
    schedule_id: str | None = None
    automation_id: str | None = None
    receipt_ids: list[str] = Field(default_factory=list)


def gateway_receipt(
    *,
    receipt_id: str,
    action: GatewayReceiptAction,
    context: GatewayReceiptContext,
    actor: str,
    capability: str,
    policy_profile: PolicyProfile,
    status: Literal["passed", "denied"],
    reason: str,
    summary: str,
    metadata: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> CapabilityReceipt:
    """Build a redacted gateway capability receipt with stable context links."""
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
                "gateway_action": action,
                **_redacted_metadata(metadata or {}),
                "redacted_fields": ["payload", "text", "body", "signature", "secret"],
            },
        ),
        redacted=True,
        created_at=now,
    )


def _target(action: GatewayReceiptAction, context: GatewayReceiptContext) -> str:
    if context.event_id:
        return f"{action}:{context.event_id}"
    if context.automation_id:
        return f"{action}:{context.automation_id}"
    if context.schedule_id:
        return f"{action}:{context.schedule_id}"
    return action


def _context_metadata(context: GatewayReceiptContext) -> dict[str, Any]:
    return {
        "channel": context.channel,
        "event_id": context.event_id,
        "policy_envelope_id": context.policy_envelope_id,
        "identity_id": context.identity_id,
        "subject": context.subject,
        "schedule_id": context.schedule_id,
        "automation_id": context.automation_id,
        "receipt_ids": context.receipt_ids,
    }


def _redacted_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    sensitive = {"payload", "text", "body", "signature", "secret"}
    return {key: value for key, value in metadata.items() if key not in sensitive}
