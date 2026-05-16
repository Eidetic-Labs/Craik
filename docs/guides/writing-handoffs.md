# Writing Handoffs

Build or inspect a case file before writing a handoff:

```sh
craik case build task_review_docs
```

Create a handoff:

```sh
craik handoff create task_review_docs \
  --summary "Reviewed docs against implementation." \
  --agent agent:codex \
  --completed-action "Compared README and docs against runtime behavior." \
  --test-run pytest \
  --next-step "Review memory backend assumptions."
```

Show the handoff:

```sh
craik handoff show task_review_docs
craik handoff show task_review_docs --markdown
```

Use `--status incomplete`, `--status blocked`, or `--status failed` when the run did not complete. Include residual risks and next steps so another agent can resume without relying on chat history.

## Required Content

Good handoffs include:

- what changed,
- what was validated,
- what assumptions remain,
- which receipts exist,
- whether any policy exceptions or fail-open paths were used,
- context debt from omitted or missing sources,
- memory proposals,
- and concrete next steps.

The handoff writer derives assumptions and context debt from the latest case file when available. It derives receipt ids from persisted receipts for the task.
