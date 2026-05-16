# Memory Proposals

Craik defaults to reviewable memory proposals instead of direct durable writes.

Create a proposal:

```sh
craik memory propose task_review_docs \
  --entity repo:example \
  --relation craik:current_state \
  --value "Local proposals require review." \
  --source README.md \
  --evidence-source README.md \
  --evidence-locator README.md#memory \
  --evidence-summary "README documents local proposal behavior."
```

List proposals:

```sh
craik memory list --task-id task_review_docs
craik memory list --status pending
```

Approve a proposal:

```sh
craik memory approve memprop_review_docs_repo_example_craik_current_state \
  --decided-by user:reviewer \
  --reason "Evidence supports the proposal."
```

Reject a proposal:

```sh
craik memory reject memprop_review_docs_repo_example_craik_current_state \
  --decided-by user:reviewer \
  --reason "Too broad for durable memory."
```

Search approved local facts:

```sh
craik memory search "local proposals"
```

## Promotion Rules

Promotion requires evidence. A proposal without evidence cannot be approved.

Pending and rejected proposals are not returned as facts. They remain in local state for audit and later review.

Direct durable writes require a future policy-granted path. Until that exists, use proposals.

## During Runs

Runner step observations are stored as `craik.run_output` records before they
become memory. A run output can create reviewable proposals, but it cannot write
durable facts directly.

Run-created proposals keep links to the originating `run_id`, `step_id`, and
optional `handoff_id`. Their evidence points back to the run output and step
result so reviewers can inspect the observed output before approval.

Blocked or failed step results are still captured for inspection, but they do
not create memory proposals. Completed and partial step results may create
proposals when the executor supplies explicit proposal specs.
