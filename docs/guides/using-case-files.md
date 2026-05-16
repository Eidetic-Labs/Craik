# Using Case Files

Case files require a registered project and a persisted task.

Register a Git repository:

```sh
craik project add /path/to/repo --name Example
```

Create a task:

```sh
craik task create \
  --project Example \
  --title "Review docs" \
  --objective "Review docs against implementation." \
  --mode review
```

Build the case file:

```sh
craik case build task_review_docs
```

Show it later by task id or case file id:

```sh
craik case show task_review_docs
craik case show case_review_docs
```

Review these fields before starting work:

- `objective`
- `policy_envelope_id`
- `repo_state`
- `docs`
- `adrs`
- `evidence`
- `assumptions`
- `stale_risks`
- `context_budget`

Open assumptions mean the case file is useful but incomplete. Downstream agents should keep those assumptions visible in plans, findings, and handoffs until evidence resolves them.
