# Memory Impact Preview

Craik previews memory impact before promotion or direct Stigmem writes.

Print a preview for a task:

```sh
craik memory preview task_review_docs
```

The preview shows:

- facts that would be added,
- facts that would be invalidated,
- likely contradictions against existing approved local facts,
- proposals missing evidence,
- and scope visibility counts.

The preview is intentionally explicit about memory scope. Before granting a direct `memory.write`, reviewers should confirm the scope, evidence, and contradiction risk are acceptable.

Direct Stigmem writes still require a matching `memory.write` grant. When that grant is absent, agents should leave memory proposals instead.
