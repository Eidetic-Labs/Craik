"""Webhook ingress validation and parsing for the gateway."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime
from typing import Any, Literal

from craik.contracts.models import CapabilityReceipt, CraikModel, PolicyProfile, ReceiptResult

WebhookIngressStatus = Literal["accepted", "invalid", "duplicate", "unauthorized"]


class WebhookIngressResult(CraikModel):
    """Inspectable result of validating one webhook request."""

    status: WebhookIngressStatus
    accepted: bool
    reason: str
    event_id: str | None = None
    event_type: str | None = None
    dispatch_payload: dict[str, Any] = {}


def validate_webhook_request(
    *,
    body: bytes,
    headers: dict[str, str],
    secret: str,
    allowed_event_types: set[str],
    seen_event_ids: set[str],
) -> WebhookIngressResult:
    """Validate and parse one webhook request without dispatching side effects."""
    signature = headers.get("X-Craik-Signature") or headers.get("x-craik-signature")
    if not signature or not _signature_valid(body=body, secret=secret, signature=signature):
        return WebhookIngressResult(
            status="invalid",
            accepted=False,
            reason="webhook signature is missing or invalid",
        )

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return WebhookIngressResult(
            status="invalid",
            accepted=False,
            reason="webhook body is not valid JSON",
        )
    if not isinstance(payload, dict):
        return WebhookIngressResult(
            status="invalid",
            accepted=False,
            reason="webhook body must be a JSON object",
        )

    event_id = _optional_string(payload.get("event_id"))
    event_type = _optional_string(payload.get("event_type"))
    if event_id is None or event_type is None:
        return WebhookIngressResult(
            status="invalid",
            accepted=False,
            reason="webhook event requires event_id and event_type",
        )
    if event_id in seen_event_ids:
        return WebhookIngressResult(
            status="duplicate",
            accepted=False,
            reason="webhook event was already seen",
            event_id=event_id,
            event_type=event_type,
        )
    if event_type not in allowed_event_types:
        return WebhookIngressResult(
            status="unauthorized",
            accepted=False,
            reason=f"webhook event_type {event_type!r} is not allowed",
            event_id=event_id,
            event_type=event_type,
        )

    return WebhookIngressResult(
        status="accepted",
        accepted=True,
        reason="webhook event accepted for safe dispatch",
        event_id=event_id,
        event_type=event_type,
        dispatch_payload={
            "event_id": event_id,
            "event_type": event_type,
            "payload": payload.get("payload") if isinstance(payload.get("payload"), dict) else {},
        },
    )


def webhook_ingress_receipt(
    *,
    result: WebhookIngressResult,
    task_id: str,
    actor: str,
    policy_profile: PolicyProfile,
    policy_envelope_id: str,
    created_at: datetime | None = None,
) -> CapabilityReceipt:
    """Build a redacted receipt for a webhook ingress decision."""
    now = created_at or datetime.now(UTC)
    event_id = result.event_id or "unknown"
    return CapabilityReceipt(
        id=f"receipt_webhook_ingress_{result.status}_{event_id}",
        task_id=task_id,
        actor=actor,
        capability="webhook.ingress",
        target=f"webhook:{event_id}",
        policy_profile=policy_profile,
        fail_open=False,
        reason=result.reason,
        result=ReceiptResult(
            status="passed" if result.accepted else "denied",
            summary=f"Webhook ingress {result.status}.",
            metadata={
                "policy_envelope_id": policy_envelope_id,
                "event_id": result.event_id,
                "event_type": result.event_type,
                "ingress_status": result.status,
                "redacted_fields": ["body", "signature", "payload"],
            },
        ),
        redacted=True,
        created_at=now,
    )


def webhook_signature(body: bytes, secret: str) -> str:
    """Return the expected sha256 webhook signature header value."""
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _signature_valid(*, body: bytes, secret: str, signature: str) -> bool:
    expected = webhook_signature(body, secret)
    return hmac.compare_digest(signature, expected)


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None
