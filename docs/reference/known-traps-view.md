# Known Traps View

The known traps view is a read-only operator display for known traps and
negative knowledge.

The v0.7.0 TUI surface formats:

- trap statement, kind, project, task, and status;
- avoidance guidance;
- evidence, handoff, and contradiction links;
- expiry timestamps;
- negative knowledge scope and trust class.

## State Boundaries

Known traps display active, expired, and contradicted states separately.
Negative knowledge displays active, expired, and contradicted states based on
expiry and contradiction links.

Expired records remain visible for audit, but they should not be treated as
current guidance without review. Contradicted records remain visible so an
operator can inspect the conflict before relying on the trap or negative
statement.

## Review Boundary

Known traps and negative knowledge are evidence-backed review aids. They help
agents avoid repeated mistakes, but they do not override policy, resolve
contradictions, or prove absence without the cited evidence.

See [Known Traps And Negative Knowledge](known-traps.md) for the underlying
contract behavior.
