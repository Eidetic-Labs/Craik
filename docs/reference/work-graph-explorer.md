# Work Graph Explorer

The work graph explorer is a read-only operator view over
`craik.work_graph_export` and `craik.work_graph_event` records.

The v0.8.0 TUI surface formats:

- graph id and task scope;
- node count and edge count;
- node rows with id, type, task, and label;
- edge rows with source, relationship type, target, and sorted metadata.

The explorer should help operators scan dependencies, blockers,
contradictions, supersession, implementation links, and verification links
without reading raw logs.

## Boundaries

The work graph explorer must not mutate graph state. It reads exported graph
records and graph events from the local store and displays missing data as an
empty graph or absent metadata.

See [Operator Surface](operator-surface.md) for the TUI-first decision and the
shared read-only boundary.
