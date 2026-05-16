# Contradiction Inbox View

The contradiction inbox is a read-only operator view over
`craik.contradiction_report` records.

The v0.8.0 TUI surface formats:

- inbox count;
- contradiction id and status;
- task id;
- owner or unassigned state;
- summary;
- proposed resolution;
- affected artifacts;
- evidence links.

## Statuses

The inbox should display open, resolved, and ignored contradiction reports. The
view is review-oriented: it surfaces the state and supporting links but does not
resolve, ignore, or mutate contradictions.

## Boundaries

Missing owners render as `unassigned`. Missing artifact or evidence links render
as `none`. Operators should use the linked evidence and affected artifacts before
promoting any resolution to durable memory.

See [Operator Surface](operator-surface.md) for the shared TUI boundary.
