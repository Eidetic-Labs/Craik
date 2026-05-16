from datetime import UTC, datetime

from craik.runtime.gateway_receipts import GatewayReceiptContext, gateway_receipt

NOW = datetime(2026, 5, 16, 19, 45, tzinfo=UTC)


def _context() -> GatewayReceiptContext:
    return GatewayReceiptContext(
        channel="messaging",
        event_id="message_1",
        task_id="task_gateway",
        policy_envelope_id="policy_channel",
        identity_id="channel_identity_alice",
        subject="user:alice",
        receipt_ids=["receipt_prior"],
    )


def test_gateway_receipt_records_success_context() -> None:
    receipt = gateway_receipt(
        receipt_id="receipt_gateway_inbound_message_1",
        action="inbound_event",
        context=_context(),
        actor="gateway:daemon",
        capability="channel.message.receive",
        policy_profile="strict",
        status="passed",
        reason="Inbound event normalized.",
        summary="Gateway handled inbound event.",
        metadata={"provider": "fixture-chat"},
        created_at=NOW,
    )

    assert receipt.result.status == "passed"
    assert receipt.target == "inbound_event:message_1"
    assert receipt.result.metadata["channel"] == "messaging"
    assert receipt.result.metadata["policy_envelope_id"] == "policy_channel"
    assert receipt.result.metadata["identity_id"] == "channel_identity_alice"
    assert receipt.result.metadata["provider"] == "fixture-chat"


def test_gateway_receipt_records_denial_context() -> None:
    receipt = gateway_receipt(
        receipt_id="receipt_gateway_denied_message_1",
        action="denial",
        context=_context(),
        actor="gateway:daemon",
        capability="shell.execute",
        policy_profile="strict",
        status="denied",
        reason="shell.execute is outside channel policy.",
        summary="Gateway denied requested action.",
        created_at=NOW,
    )

    assert receipt.result.status == "denied"
    assert receipt.capability == "shell.execute"
    assert receipt.result.metadata["gateway_action"] == "denial"
    assert receipt.result.metadata["subject"] == "user:alice"


def test_gateway_receipt_redacts_sensitive_metadata() -> None:
    receipt = gateway_receipt(
        receipt_id="receipt_gateway_redacted_message_1",
        action="dispatch_decision",
        context=_context(),
        actor="gateway:daemon",
        capability="channel.message.respond",
        policy_profile="strict",
        status="passed",
        reason="Response approved.",
        summary="Gateway approved response dispatch.",
        metadata={
            "payload": {"text": "secret"},
            "text": "secret",
            "body": "raw",
            "signature": "sha256=secret",
            "safe": "kept",
        },
        created_at=NOW,
    )

    assert receipt.redacted is True
    assert receipt.result.metadata["safe"] == "kept"
    assert "payload" not in receipt.result.metadata
    assert "text" not in receipt.result.metadata
    assert "body" not in receipt.result.metadata
    assert "signature" not in receipt.result.metadata
    assert "payload" in receipt.result.metadata["redacted_fields"]
