# Gateway Troubleshooting

This guide covers v0.9.0 gateway surfaces: setup, diagnostics, channels,
webhooks, schedules, policies, and receipts.

## Baseline Checks

Run:

```sh
craik doctor
```

Expected output is JSON with checks for local home, local store, memory backend
configuration, gateway prerequisites, and gateway policy readiness.

Run:

```sh
craik setup --disable-gateway
```

Expected output includes `secrets_written = false` and a local-only gateway
configuration. Do not put channel tokens, webhook secrets, or bearer credentials
in Craik config payloads.

## Setup Problems

| Symptom | Check | Resolution |
| --- | --- | --- |
| Gateway config is missing | `craik doctor` reports gateway config warnings | Run `craik setup` and review the JSON output. |
| Public bind is rejected | Setup or validation reports missing policy | Add a policy envelope before using a public bind host. |
| Secrets appear in output | Review setup output and receipts | Move secrets to the provider-specific secret store and rotate exposed credentials. |

See [Setup Wizard](setup.md), [Doctor Diagnostics](doctor.md), and
[Gateway Daemon Mode](../reference/gateway-daemon.md).

## Channel Problems

| Symptom | Check | Resolution |
| --- | --- | --- |
| Message is normalized but not authorized | Inspect pairing, allowlist, and policy decisions | Pair the identity, add an allowlist rule, then select a channel policy. |
| Sender remains unpaired | Inspect channel identity pairing state | Complete an explicit pairing flow with audit links. |
| Sender was revoked | Pairing state is `revoked` | Create a new approved pairing if access should be restored. |
| Event is denied by allowlist | Decision reason is `no enabled allowlist rule matched` | Add or enable a narrow rule for the sender, workspace, thread, or metadata. |

See [Channel Adapter Contract](../reference/channel-adapter-contract.md),
[Messaging Channel Adapter](../reference/messaging-channel-adapter.md),
[Channel Identity Pairing](../reference/channel-identity-pairing.md),
[Channel Allowlists](../reference/channel-allowlists.md), and
[Channel Policy Envelopes](../reference/channel-policy-envelopes.md).

## Webhook Problems

| Symptom | Check | Resolution |
| --- | --- | --- |
| Request is invalid | Ingress reason says signature is missing or invalid | Recompute the `X-Craik-Signature` value over the raw body. |
| Body is rejected | Ingress reason says body is not a JSON object | Send a JSON object with `event_id` and `event_type`. |
| Event is duplicate | Ingress status is `duplicate` | Treat the event as already handled; do not dispatch twice. |
| Event type is unauthorized | Ingress status is `unauthorized` | Add the event type to the configured allowlist only if it is intended. |

See [Webhook Ingress](../reference/webhook-ingress.md).

## Schedule Problems

| Symptom | Check | Resolution |
| --- | --- | --- |
| Schedule is rejected | Validation says five fields are required | Use a five-field cron-like expression. |
| Schedule token is rejected | Validation reports unsupported cron field | Use only digits, `*`, `/`, `,`, and `-`. |
| Task is not created | Result says tick already created a task | Use the existing task for that tick. |
| Automation does not run | Result status is `disabled` | Enable the automation after reviewing policy and receipts. |
| Automation is policy denied | Result status is `policy_denied` | Add `gateway.schedule.execute` only to the intended policy envelope. |

See [Scheduled Task Creation](../reference/scheduled-task-creation.md) and
[Scheduled Automations](../reference/scheduled-automations.md).

## Policy And Receipt Problems

| Symptom | Check | Resolution |
| --- | --- | --- |
| Channel action is denied | Receipt status is `denied` | Inspect requested capability and channel policy boundaries. |
| Local operator capability is unavailable | Policy denies `shell.execute`, `repo.write`, or similar | Use a local operator workflow instead of channel ingress. |
| Receipt lacks payload text | `redacted_fields` includes payload fields | This is expected; gateway receipts omit sensitive channel data. |
| Receipt link is missing | Check policy, channel, task, and identity ids | Recreate the gateway decision with complete context before dispatch. |

See [Gateway Receipts](../reference/gateway-receipts.md), [Policy Profiles](../reference/policy-profiles.md),
and [Receipt Viewer](../reference/receipt-viewer.md).

## Safe Diagnostic Commands

Use commands that inspect state without exposing secrets:

```sh
craik doctor
craik setup --disable-gateway
craik update
```

For development validation, run:

```sh
uv run --extra dev ruff check .
uv run --extra dev mypy
uv run --extra dev pytest
```

Do not paste webhook secrets, bearer tokens, raw message bodies, or provider
signing secrets into issue reports, public docs, or receipts.
