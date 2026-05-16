from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.contracts.models import ChannelAdapterContract
from craik.contracts.registry import schema_model


def _contract(**overrides: object) -> ChannelAdapterContract:
    payload: dict[str, object] = {
        "schema": "craik.channel_adapter_contract",
        "version": "0.1.0",
        "id": "channel_adapter_messaging_fixture",
        "identity": {
            "adapter_id": "messaging_fixture",
            "channel": "messaging",
            "name": "Messaging Fixture Adapter",
            "adapter_version": "0.1.0",
            "service": "fixture-chat",
        },
        "capabilities": [
            {
                "name": "channel.message.receive",
                "direction": "inbound",
                "description": "Receive normalized operator messages.",
                "grant_required": True,
                "receipt_required": True,
            },
            {
                "name": "channel.message.respond",
                "direction": "outbound",
                "description": "Send redacted operator responses.",
                "grant_required": True,
                "receipt_required": True,
            },
        ],
        "inbound_event": {
            "fields": [
                "event_id",
                "channel",
                "received_at",
                "sender",
                "text",
                "thread_id",
            ],
            "redacted_fields": ["text"],
        },
        "outbound_response": {
            "fields": ["response_id", "event_id", "status", "summary", "text", "receipt_ids"],
            "redacted_fields": ["text"],
        },
        "receipts": {
            "required": True,
            "receipt_schema": "craik.capability_receipt",
            "capabilities": ["channel.message.receive", "channel.message.respond"],
        },
        "trust_boundary": {
            "policy_envelope_required": True,
            "allowlist_required": True,
            "inbound_identity_required": True,
            "secrets_in_config_allowed": False,
            "notes": ["Adapters normalize payloads but do not grant authority."],
        },
        "docs": ["docs/reference/channel-adapter-contract.md"],
        "created_at": datetime(2026, 5, 16, 18, 30, tzinfo=UTC),
    }
    payload.update(overrides)
    return ChannelAdapterContract.model_validate(payload)


def test_channel_adapter_contract_registers_schema() -> None:
    assert schema_model("craik.channel_adapter_contract") is ChannelAdapterContract


def test_channel_adapter_contract_validates_core_fields() -> None:
    contract = _contract()

    assert contract.identity.channel == "messaging"
    assert contract.capabilities[0].name == "channel.message.receive"
    assert contract.receipts.required is True
    assert contract.trust_boundary.policy_envelope_required is True
    assert contract.trust_boundary.secrets_in_config_allowed is False


def test_channel_adapter_contract_requires_inbound_identity_shape() -> None:
    with pytest.raises(ValidationError, match="sender"):
        _contract(
            inbound_event={
                "fields": ["event_id", "channel", "received_at", "text"],
                "redacted_fields": ["text"],
            }
        )


def test_channel_adapter_contract_requires_declared_receipt_capabilities() -> None:
    with pytest.raises(ValidationError, match="not declared"):
        _contract(
            receipts={
                "required": True,
                "receipt_schema": "craik.capability_receipt",
                "capabilities": ["channel.unknown"],
            }
        )


def test_channel_adapter_contract_preserves_policy_boundary() -> None:
    with pytest.raises(ValidationError, match="policy envelopes"):
        _contract(
            trust_boundary={
                "policy_envelope_required": False,
                "allowlist_required": True,
                "inbound_identity_required": True,
                "secrets_in_config_allowed": False,
            }
        )
