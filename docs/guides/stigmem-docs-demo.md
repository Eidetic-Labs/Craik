# Stigmem Documentation Reconciliation Demo

Craik's first runnable demo reconciles Stigmem documentation and observed runtime
state without editing files by default.

The workflow:

- registers the Stigmem repository as a Craik project,
- optionally checks a local Stigmem node,
- creates a documentation reconciliation task,
- assembles a case file from repository docs, ADRs, repo state, and optional GitHub state,
- surfaces stale-risk and boundary findings,
- proposes public-safe documentation updates,
- records a receipt,
- creates a handoff,
- creates a local memory proposal,
- records the memory write path as a reviewable proposal instead of a direct
  write,
- opens a local contradiction report,
- executes deterministic OpenAI and Anthropic provider-backed runner paths,
- and exports a task-scoped work graph.

## Run It

From a Stigmem repository checkout:

```sh
export CRAIK_HOME=/tmp/craik-demo
export CRAIK_STIGMEM_URL=http://127.0.0.1:18765
export CRAIK_STIGMEM_API_KEY=<api-key>

uv run --python 3.12 --extra dev craik demo stigmem-docs --repo-path .
```

For an offline local run without GitHub or live Stigmem:

```sh
uv run --python 3.12 --extra dev craik demo stigmem-docs --repo-path . --no-github
```

That offline command is the quickstart smoke path used by CI.

To limit deterministic provider execution to one provider while debugging:

```sh
uv run --python 3.12 --extra dev craik demo stigmem-docs --repo-path . --no-github --provider-id provider_openai
```

The command prints a `craik.demo.stigmem_docs_reconciliation` JSON payload.

## Expected Artifacts

The demo creates deterministic local records:

- project: `project_stigmem`,
- task: `task_stigmem_documentation_reconciliation`,
- case file: `case_stigmem_documentation_reconciliation`,
- receipt: `receipt_demo_stigmem_documentation_reconciliation`,
- handoff: `handoff_stigmem_documentation_reconciliation`,
- graph: `graph_task_stigmem_documentation_reconciliation`,
- one local memory proposal,
- and one local contradiction report.
- provider-backed OpenAI and Anthropic run summaries under
  `provider_executions`.

Inspect follow-up artifacts:

```sh
craik case show task_stigmem_documentation_reconciliation
craik contradictions list --task-id task_stigmem_documentation_reconciliation
craik memory list --task-id task_stigmem_documentation_reconciliation
craik handoff show task_stigmem_documentation_reconciliation
craik graph export --task-id task_stigmem_documentation_reconciliation
```

## Boundary Behavior

The demo treats ADRs and configured immutable paths as evidence. It does not edit
repository files. Proposed documentation updates are emitted as reviewable
suggestions in the JSON payload.

The demo also surfaces public/internal boundaries. Public docs should not receive
internal-only labels, private planning names, local filesystem paths, or secrets.

## Memory Behavior

The demo creates a local memory proposal. It does not write directly to Stigmem
because direct durable memory writes require explicit policy grants. This keeps
the workflow safe for first runs and CI. The JSON payload includes
`memory_write.status = "proposal_created"` so release acceptance can verify that
the memory write path remained explicit.

## Provider Behavior

The demo exercises `provider_openai` and `provider_anthropic` through the
deterministic provider-backed runner. These runs normalize provider payloads,
record provider receipts, create run-scoped handoffs, and do not require live
OpenAI or Anthropic credentials.

## Expected Output Shape

```json
{
  "schema": "craik.demo.stigmem_docs_reconciliation",
  "status": "runnable",
  "case_file_id": "case_stigmem_documentation_reconciliation",
  "receipt_ids": ["receipt_demo_stigmem_documentation_reconciliation"],
  "handoff_id": "handoff_stigmem_documentation_reconciliation",
  "memory_proposal_ids": ["memprop_..."],
  "memory_write": {"status": "proposal_created"},
  "contradiction_ids": ["contradiction_..."],
  "provider_executions": [
    {"provider_id": "provider_openai", "run_status": "completed"},
    {"provider_id": "provider_anthropic", "run_status": "completed"}
  ],
  "work_graph_id": "graph_task_stigmem_documentation_reconciliation"
}
```

## Troubleshooting

If Stigmem is not running, the demo still runs and reports
`stigmem_backend_status.status = "not_configured"` or `"error"`.

If GitHub is unavailable, use `--no-github`. The case file will include an open
assumption or stale-risk warning that GitHub state was not loaded.

If no ADRs are discovered, confirm the repository has `docs/adr/` or pass
project registration options in a separate setup step when those are available.

If a run fails because the path is not a Git repository, pass `--repo-path` to a
directory inside the Stigmem checkout.
