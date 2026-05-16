# Receipt Viewer

The receipt viewer is a read-only operator view over capability and plugin
receipt records.

The v0.8.0 TUI surface formats capability receipts with:

- receipt id, task, actor, capability, target, and policy profile;
- status, reason, redacted summary, and redaction state.

It formats plugin receipts with:

- receipt id, task, actor, plugin descriptor, action, and trust boundary;
- status, redacted summary, and redaction state;
- linked capability grants, evidence, and handoffs.

## Outcomes

The receipt viewer should display `passed`, `failed`, `denied`, and `skipped`
statuses without expanding raw command output or unredacted plugin output.

## Boundaries

The receipt viewer is for inspection only. It does not approve grants, retry
commands, rerun plugins, or mutate receipt records.

See [Operator Surface](operator-surface.md) for the shared TUI boundary.
