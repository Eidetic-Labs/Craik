# Run Delta View

The run delta view is a read-only operator display for continuity-relevant
changes since the previous usable handoff or resume point.

The v0.7.0 TUI surface formats:

- previous and current handoff links;
- case file, receipt, contradiction, and active instruction constraint links;
- created, updated, removed, and unchanged change items;
- recovery sessions linked to the run delta;
- required actions and stale-risk warnings for non-clean recovery.

## Inspection Boundary

Run deltas summarize already persisted local state. The view does not inspect
the working tree, refresh GitHub, query Stigmem, or decide whether a run can
continue. Operators should refresh those sources separately and persist the
resulting receipts, handoffs, contradictions, or recovery sessions.

## Recovery Links

Recovery sessions explain how a resume should treat the delta. A clean session
may have no required actions. Changed or missing context must show required
actions so agents do not continue silently through stale or incomplete state.

See [Recovery Mode](recovery.md) for the underlying contract behavior.
