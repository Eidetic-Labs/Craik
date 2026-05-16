# Contradiction Inbox

Craik keeps local contradiction reports for conflicts that are not necessarily Stigmem-level conflicts.

Open a report:

```sh
craik contradictions open \
  --task-id task_review_docs \
  --summary "Docs conflict with implementation." \
  --fact fact_docs_planned \
  --fact fact_cli_implemented \
  --affected-artifact README.md \
  --evidence-id evidence_readme_status \
  --owner user:maintainer
```

List open reports:

```sh
craik contradictions list --status open
```

Show one report and linked local evidence:

```sh
craik contradictions show contradiction_task_review_docs_docs_conflict_with_implementation
```

Contradiction reports include:

- conflicting fact ids or statements,
- affected artifacts,
- evidence ids,
- owner,
- proposed resolution,
- status,
- and an optional future `stigmem_conflict_id`.

Reports are local workflow items. They are redacted before storage and appear in work graph exports when linked to a task.

## Local Reports And Stigmem Conflicts

Stigmem conflicts are memory-substrate conflicts. Craik local contradiction reports are broader workflow conflicts, such as:

- docs disagreeing with implementation,
- a handoff disagreeing with branch state,
- a reviewer result disagreeing with an implementer result,
- or public docs containing content that should stay internal.

When a Stigmem conflict exists, store its id in `stigmem_conflict_id`. Resolving Stigmem conflicts remains future work and should require explicit memory-write authority.
