"""Channel allowlist evaluation for normalized inbound events."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from craik.contracts.models import (
    CapabilityReceipt,
    ChannelAllowlist,
    ChannelAllowlistRule,
    ChannelKind,
    CraikModel,
    PolicyProfile,
    ReceiptResult,
)


class ChannelAllowlistDecision(CraikModel):
    """Inspectable allowlist decision for one inbound channel event."""

    allowed: bool
    reason: str
    rule_id: str | None = None
    event_id: str | None = None
    channel: ChannelKind | None = None
    sender_external_id: str | None = None


def evaluate_channel_allowlist(
    allowlist: ChannelAllowlist,
    event: dict[str, Any],
) -> ChannelAllowlistDecision:
    """Evaluate a normalized inbound event against a deny-by-default allowlist."""
    event_channel = _optional_string(event.get("channel"))
    if event_channel != allowlist.channel:
        return _deny(event, f"event channel {event_channel!r} does not match allowlist")

    for rule in allowlist.rules:
        if rule.enabled and _rule_matches(rule, event):
            return ChannelAllowlistDecision(
                allowed=True,
                reason=f"matched allowlist rule {rule.id}",
                rule_id=rule.id,
                event_id=_optional_string(event.get("event_id")),
                channel=allowlist.channel,
                sender_external_id=_sender_external_id(event),
            )

    return _deny(event, "no enabled allowlist rule matched")


def allowlist_denial_receipt(
    *,
    decision: ChannelAllowlistDecision,
    allowlist: ChannelAllowlist,
    task_id: str,
    actor: str,
    policy_profile: PolicyProfile,
    policy_envelope_id: str,
    created_at: datetime | None = None,
) -> CapabilityReceipt:
    """Build a redacted denial receipt for a rejected inbound channel event."""
    if decision.allowed:
        raise ValueError("allowlist denial receipt requires a denied decision")
    now = created_at or datetime.now(UTC)
    event_id = decision.event_id or "unknown"
    return CapabilityReceipt(
        id=f"receipt_channel_allowlist_denied_{event_id}",
        task_id=task_id,
        actor=actor,
        capability=allowlist.denial_capability,
        target=f"{allowlist.channel}:{event_id}",
        policy_profile=policy_profile,
        fail_open=False,
        reason=decision.reason,
        result=ReceiptResult(
            status="denied",
            summary="Inbound channel event denied by allowlist.",
            metadata={
                "policy_envelope_id": policy_envelope_id,
                "allowlist_id": allowlist.id,
                "event_id": decision.event_id,
                "channel": decision.channel,
                "sender_external_id": decision.sender_external_id,
                "redacted_fields": ["text"],
            },
        ),
        redacted=True,
        created_at=now,
    )


def _rule_matches(rule: ChannelAllowlistRule, event: dict[str, Any]) -> bool:
    metadata = event.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    sender_external_id = _sender_external_id(event)
    if rule.channel is not None and _optional_string(event.get("channel")) != rule.channel:
        return False
    if rule.service is not None and _optional_string(metadata.get("service")) != rule.service:
        return False
    if rule.sender_external_ids and sender_external_id not in rule.sender_external_ids:
        return False
    if rule.workspace_ids and _optional_string(metadata.get("workspace")) not in rule.workspace_ids:
        return False
    if rule.thread_ids and _optional_string(event.get("thread_id")) not in rule.thread_ids:
        return False
    for key, expected in rule.metadata_match.items():
        if _optional_string(metadata.get(key)) != expected:
            return False
    return True


def _deny(event: dict[str, Any], reason: str) -> ChannelAllowlistDecision:
    channel = _optional_string(event.get("channel"))
    known_channel = (
        cast(ChannelKind, channel)
        if channel in {"messaging", "webhook", "scheduler", "voice", "custom"}
        else None
    )
    return ChannelAllowlistDecision(
        allowed=False,
        reason=reason,
        event_id=_optional_string(event.get("event_id")),
        channel=known_channel,
        sender_external_id=_sender_external_id(event),
    )


def _sender_external_id(event: dict[str, Any]) -> str | None:
    sender = event.get("sender")
    if isinstance(sender, dict):
        return _optional_string(sender.get("external_id"))
    return None


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None
