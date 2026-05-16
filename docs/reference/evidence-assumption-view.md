# Evidence And Assumption View

The evidence and assumption view is a read-only operator view over
`craik.evidence_reference` and `craik.assumption` records.

The v0.8.0 TUI surface formats evidence with:

- evidence id and kind;
- source and locator;
- capture timestamp when present;
- summary.

It formats assumptions separately with:

- assumption id and status;
- task id;
- confidence;
- linked evidence ids;
- statement.

## Boundaries

Assumptions are not facts. The view must keep assumptions visually separate from
evidence and must show confidence and status so operators can review whether an
assumption is open, validated, or rejected.

Missing evidence or assumptions render as `none`. The view does not validate,
reject, promote, or write memory facts.

See [Operator Surface](operator-surface.md) for the shared TUI boundary.
