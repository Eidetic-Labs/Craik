# Delegation Queue View

The delegation queue is a read-only operator view over
`craik.human_delegation_point` records.

The v0.7.0 TUI surface formats:

- delegation count;
- delegation id, status, and kind;
- task id;
- owner or unassigned state;
- requester;
- requested decision;
- summary;
- policy envelope link;
- receipt links;
- resolution when present.

## Statuses

The queue should display open, resolved, and cancelled delegation points. Open
items should make pending approvals, clarifications, escalations, or ownership
transfers easy to find.

## Boundaries

The queue does not approve, cancel, or resolve delegation points. It shows
auditable state so operators know where human input is needed or already
recorded.

See [Operator Surface](operator-surface.md) for the shared TUI boundary.
