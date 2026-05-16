from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.contracts.models import ChannelAllowlist, ChannelAllowlistRule
from craik.contracts.registry import schema_model
from craik.runtime.channel_allowlist import (
    allowlist_denial_receipt,
    evaluate_channel_allowlist,
)
from craik.runtime.messaging_channel import normalize_inbound_message

NOW = datetime(2026, 5, 16, 18, 55, tzinfo=UTC)


def _allowlist() -> ChannelAllowlist:
    return ChannelAllowlist.model_validate(
        {
            "schema": "craik.channel_allowlist",
            "version": "0.1.0",
            "id": "allowlist_messaging_ops",
            "channel": "messaging",
            "default_action": "deny",
            "rules": [
                {
                    "id": "ops_alice",
                    "description": "Allow Alice in ops workspace.",
                    "channel": "messaging",
                    "sender_external_ids": ["external:alice"],
                    "workspace_ids": ["ops"],
                    "enabled": True,
                }
            ],
            "audit_required": True,
            "denial_capability": "channel.ingress.denied",
            "created_at": NOW,
            "updated_at": NOW,
        }
    )


def test_channel_allowlist_registers_schema() -> None:
    assert schema_model("craik.channel_allowlist") is ChannelAllowlist


def test_channel_allowlist_allows_matching_inbound_event() -> None:
    event = normalize_inbound_message(
        event_id="message_1",
        sender_id="external:alice",
        text="run status",
        received_at=NOW,
        metadata={"workspace": "ops"},
    )

    decision = evaluate_channel_allowlist(_allowlist(), event)

    assert decision.allowed is True
    assert decision.rule_id == "ops_alice"
    assert decision.sender_external_id == "external:alice"


def test_channel_allowlist_denies_unmatched_sender_with_reason() -> None:
    event = normalize_inbound_message(
        event_id="message_2",
        sender_id="external:bob",
        text="run status",
        received_at=NOW,
        metadata={"workspace": "ops"},
    )

    decision = evaluate_channel_allowlist(_allowlist(), event)

    assert decision.allowed is False
    assert decision.reason == "no enabled allowlist rule matched"
    assert decision.sender_external_id == "external:bob"


def test_channel_allowlist_denies_wrong_channel() -> None:
    event = normalize_inbound_message(
        event_id="message_3",
        sender_id="external:alice",
        text="run status",
        received_at=NOW,
        metadata={"workspace": "ops"},
    )
    event["channel"] = "webhook"

    decision = evaluate_channel_allowlist(_allowlist(), event)

    assert decision.allowed is False
    assert "does not match allowlist" in decision.reason


def test_channel_allowlist_denial_receipt_redacts_payload() -> None:
    event = normalize_inbound_message(
        event_id="message_2",
        sender_id="external:bob",
        text="run status",
        received_at=NOW,
        metadata={"workspace": "ops"},
    )
    decision = evaluate_channel_allowlist(_allowlist(), event)

    receipt = allowlist_denial_receipt(
        decision=decision,
        allowlist=_allowlist(),
        task_id="task_gateway",
        actor="adapter:messaging_fixture",
        policy_profile="strict",
        policy_envelope_id="policy_gateway",
        created_at=NOW,
    )

    assert receipt.capability == "channel.ingress.denied"
    assert receipt.result.status == "denied"
    assert receipt.result.metadata["allowlist_id"] == "allowlist_messaging_ops"
    assert receipt.result.metadata["sender_external_id"] == "external:bob"
    assert "text" not in receipt.result.metadata


def test_channel_allowlist_rejects_allow_by_default() -> None:
    with pytest.raises(ValidationError, match="default to deny"):
        ChannelAllowlist.model_validate(
            {
                "schema": "craik.channel_allowlist",
                "version": "0.1.0",
                "id": "allowlist_bad",
                "channel": "messaging",
                "default_action": "allow",
                "created_at": NOW,
                "updated_at": NOW,
            }
        )


def test_channel_allowlist_rule_requires_selector() -> None:
    with pytest.raises(ValidationError, match="at least one selector"):
        ChannelAllowlistRule(id="too_broad", description="Too broad")
