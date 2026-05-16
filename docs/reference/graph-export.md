# Graph Export

Export the local work graph:

```sh
craik graph export
```

Export graph objects for one task:

```sh
craik graph export --task-id task_review_docs
```

The command prints a `craik.work_graph_export` payload:

- `nodes`: graph nodes with `id`, `type`, `label`, optional `task_id`, and redacted metadata.
- `edges`: graph edges with `id`, `type`, `from`, `to`, and redacted metadata.

Task-scoped exports include connected local objects for the requested task. Repository-wide exports include all graph-compatible local objects in the current Craik home.

Graph export currently derives from local store contracts. Future runtime workflows can add more `craik.work_graph_event` records to connect delegated work, external artifacts, and review decisions.
