# Capability Grants

Craik does not give agents ambient authority. Side effects require capability grants.

Grant checks return one of three practical outcomes:

- allowed by a matching grant,
- denied,
- or denied until explicit approval metadata and a matching grant exist.

## File Writes

Normal documentation writes require `repo.write.docs` with a matching path and `write` operation.

Example grant shape:

```json
{
  "schema": "craik.capability_grant",
  "version": "0.1.0",
  "id": "grant_docs_write",
  "task_id": "task_docs",
  "capability": "repo.write.docs",
  "target": {
    "paths": ["docs/**"],
    "exclude": ["docs/adr/**"]
  },
  "operations": ["write"],
  "reason": "Documentation update.",
  "approved_by": "user:maintainer"
}
```

## Immutable Paths

Immutable paths, such as ADR directories, are denied by default.

Writing an immutable path requires both:

- explicit override metadata with `approved_by` and `reason`,
- and a matching `repo.write.immutable` grant.

Override metadata alone is not enough.

## Shell, GitHub, And Memory Hooks

Craik also exposes policy hooks for:

- `shell.execute`,
- `github.write`,
- `memory.write`.

The v0.1.0 hook layer checks whether a matching grant exists. Runtime provider
and tool-call paths call these checks before performing side effects.

Denied decisions can produce capability receipts with status `denied`.
