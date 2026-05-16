import json
from datetime import UTC, datetime

from craik.runtime.webhook_ingress import (
    validate_webhook_request,
    webhook_ingress_receipt,
    webhook_signature,
)

NOW = datetime(2026, 5, 16, 19, 15, tzinfo=UTC)
SECRET = "webhook-secret"


def _body(event_id: str = "webhook_1", event_type: str = "message.created") -> bytes:
    return json.dumps(
        {
            "event_id": event_id,
            "event_type": event_type,
            "payload": {"text": "run status"},
        }
    ).encode("utf-8")


def _headers(body: bytes) -> dict[str, str]:
    return {"X-Craik-Signature": webhook_signature(body, SECRET)}


def test_webhook_ingress_accepts_valid_authorized_event() -> None:
    body = _body()

    result = validate_webhook_request(
        body=body,
        headers=_headers(body),
        secret=SECRET,
        allowed_event_types={"message.created"},
        seen_event_ids=set(),
    )

    assert result.accepted is True
    assert result.status == "accepted"
    assert result.event_id == "webhook_1"
    assert result.event_type == "message.created"
    assert result.dispatch_payload["payload"] == {"text": "run status"}


def test_webhook_ingress_rejects_invalid_signature() -> None:
    result = validate_webhook_request(
        body=_body(),
        headers={"X-Craik-Signature": "sha256:bad"},
        secret=SECRET,
        allowed_event_types={"message.created"},
        seen_event_ids=set(),
    )

    assert result.accepted is False
    assert result.status == "invalid"
    assert result.reason == "webhook signature is missing or invalid"


def test_webhook_ingress_rejects_duplicate_event() -> None:
    body = _body()

    result = validate_webhook_request(
        body=body,
        headers=_headers(body),
        secret=SECRET,
        allowed_event_types={"message.created"},
        seen_event_ids={"webhook_1"},
    )

    assert result.accepted is False
    assert result.status == "duplicate"
    assert result.event_id == "webhook_1"


def test_webhook_ingress_rejects_unauthorized_event_type() -> None:
    body = _body(event_type="workspace.deleted")

    result = validate_webhook_request(
        body=body,
        headers=_headers(body),
        secret=SECRET,
        allowed_event_types={"message.created"},
        seen_event_ids=set(),
    )

    assert result.accepted is False
    assert result.status == "unauthorized"
    assert "not allowed" in result.reason


def test_webhook_ingress_rejects_invalid_json_shape() -> None:
    body = b"[]"

    result = validate_webhook_request(
        body=body,
        headers=_headers(body),
        secret=SECRET,
        allowed_event_types={"message.created"},
        seen_event_ids=set(),
    )

    assert result.accepted is False
    assert result.status == "invalid"
    assert result.reason == "webhook body must be a JSON object"


def test_webhook_ingress_receipt_redacts_payload_and_signature() -> None:
    body = _body()
    result = validate_webhook_request(
        body=body,
        headers=_headers(body),
        secret=SECRET,
        allowed_event_types={"message.created"},
        seen_event_ids=set(),
    )

    receipt = webhook_ingress_receipt(
        result=result,
        task_id="task_gateway",
        actor="gateway:webhook",
        policy_profile="strict",
        policy_envelope_id="policy_gateway",
        created_at=NOW,
    )

    assert receipt.result.status == "passed"
    assert receipt.capability == "webhook.ingress"
    assert receipt.result.metadata["event_id"] == "webhook_1"
    assert receipt.result.metadata["event_type"] == "message.created"
    assert "payload" not in receipt.result.metadata
    assert "signature" not in receipt.result.metadata
