# Webhook Ingress

Webhook ingress validates one request boundary before any gateway dispatch.

`craik.runtime.webhook_ingress` provides pure runtime helpers for:

- HMAC SHA-256 signature validation;
- JSON object parsing;
- required `event_id` and `event_type` extraction;
- idempotency checks against known event ids;
- event type authorization;
- redacted ingress receipts.

## Signature

Requests use the `X-Craik-Signature` header with the format:

```text
sha256=<hex digest>
```

The digest is computed over the raw request body with the configured webhook
secret. Missing or invalid signatures are rejected before JSON parsing.

## Event Shape

Accepted webhook bodies are JSON objects with:

- `event_id`;
- `event_type`;
- optional object `payload`.

Only configured event types are accepted. Duplicate event ids are rejected before
dispatch.

## Safe Dispatch

Accepted results include a `dispatch_payload` containing the event id, event
type, and object payload. The helper does not perform side effects or enqueue
work by itself.

## Receipts

Webhook ingress receipts use the `webhook.ingress` capability. Receipt metadata
preserves event id, event type, policy envelope id, ingress status, and redaction
fields. Raw body, signatures, and payload content are not stored in receipt
metadata.

## Security Boundary

Webhook validation does not grant channel authority. Accepted webhook events
still need channel policy, allowlist, identity, and capability checks before any
privileged gateway action.
