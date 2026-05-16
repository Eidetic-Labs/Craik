# Gateway Receipts

Gateway receipts are redacted `craik.capability_receipt` records for always-on
service actions.

`craik.runtime.gateway_receipts` covers:

- inbound event handling;
- dispatch decisions;
- policy checks;
- denials;
- scheduled automation actions.

## Context Links

Gateway receipt metadata preserves stable links where available:

- channel;
- event id;
- task id;
- policy envelope id;
- channel identity id;
- paired subject;
- schedule id;
- automation id;
- related receipt ids.

## Redaction

Gateway receipts always set `redacted = true`. Sensitive metadata keys are
removed before receipt construction:

- `payload`;
- `text`;
- `body`;
- `signature`;
- `secret`.

The receipt records these names in `redacted_fields` so operators can see that
payload material was intentionally omitted.

## Status

Successful gateway actions use receipt result status `passed`. Denied gateway
actions use status `denied` and keep the denial reason in the receipt.

Gateway receipts do not grant authority. They only preserve an audit trail for
decisions already made by gateway policy, identity, allowlist, and scheduler
boundaries.
