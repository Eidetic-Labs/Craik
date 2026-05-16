# Scope Control

Craik uses intent locks to keep task execution aligned with the accepted request.

Create a task with explicit scope controls:

```sh
craik task create \
  --project Example \
  --title "Review docs" \
  --objective "Review docs against implementation." \
  --accepted-interpretation "Review documentation only." \
  --in-scope "README.md" \
  --in-scope "docs/" \
  --out-of-scope "ADR edits" \
  --allowed-autonomy "Inspect repository files" \
  --stop-condition "The task requires changing immutable docs" \
  --scope-change-rule "Ask before expanding beyond documentation review"
```

Inspect the lock:

```sh
craik intent show task_review_docs
```

Before acting, review:

- `accepted_interpretation`
- `in_scope`
- `out_of_scope`
- `allowed_autonomy`
- `stop_conditions`
- `scope_change_rules`

If the work crosses those boundaries, pause and update the task intent rather than silently widening scope.

## Defaults

If no explicit intent fields are supplied, Craik creates conservative defaults from the task request:

- title becomes the original request,
- objective becomes the accepted interpretation,
- expected outputs become in-scope work,
- constraints become out-of-scope work,
- and default stop conditions require stopping when project context is missing, policy conflicts, or the objective materially changes.
