# Handoff Viewer

Design rationale: [ADR 0005 Receipts And Handoffs As Public Contracts](../adr/0005-receipts-and-handoffs-as-public-contracts.md).

The handoff viewer is a read-only operator view over `craik.handoff` records.

The v0.7.0 TUI surface formats:

- handoff id, task id, project id, status, agent, and summary;
- completed actions;
- next steps;
- receipt links;
- evidence-like artifacts and changed files;
- risks;
- open follow-ups such as context debt, assumptions, contradictions, and human
  delegation ids.

## Boundaries

The handoff viewer must preserve redaction boundaries. It displays the durable
summary already captured in the handoff and linked ids for deeper inspection. It
must not read raw logs or expand potentially sensitive command output.

Missing sections should render as `none` so operators can distinguish an empty
section from a formatter failure.

See [Operator Surface](operator-surface.md) for the shared TUI boundary.
