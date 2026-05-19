# Stigmem documentation reconciliation demo

<p className="craik-meta"><span>6 min read</span><span>For first-time operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Run Craik's first end-to-end demo — reconciling Stigmem documentation
against observed runtime state without editing files by default. The
workflow exercises case-file assembly, receipts, handoffs, memory
proposals, contradictions, deterministic provider runs, and a
task-scoped work-graph export.

</div>

<div className="craik-keypoint">

**This is the accepted release-acceptance workflow.**

Every v0.x.0 candidate must pass this demo from a clean install.

</div>

## What the demo does

<div className="craik-grid">

<div><h4>Registers Stigmem repo</h4><p>As a Craik project.</p></div>
<div><h4>Checks Stigmem node</h4><p>Optional — if URL configured.</p></div>
<div><h4>Creates a reconciliation task</h4></div>
<div><h4>Assembles a case file</h4><p>Repository docs · ADRs · repo state · optional GitHub state.</p></div>
<div><h4>Surfaces findings</h4><p>Stale-risk and boundary issues.</p></div>
<div><h4>Proposes doc updates</h4><p>Public-safe suggestions only.</p></div>
<div><h4>Records a receipt</h4></div>
<div><h4>Creates a handoff</h4></div>
<div><h4>Creates a memory proposal</h4><p>Local — direct writes need a grant.</p></div>
<div><h4>Opens a contradiction report</h4><p>Local.</p></div>
<div><h4>Runs provider paths</h4><p>Deterministic OpenAI + Anthropic.</p></div>
<div><h4>Exports work graph</h4><p>Task-scoped.</p></div>

</div>

## Run it

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

<div className="craik-keypoint">

**Offline = CI quickstart smoke path.**

The `--no-github` form is the smoke path CI runs.

</div>

To limit deterministic provider execution to one provider while
debugging:

```sh
uv run --python 3.12 --extra dev craik demo stigmem-docs --repo-path . --no-github --provider-id provider_openai
```

The command prints a `craik.demo.stigmem_docs_reconciliation` JSON
payload.

## Expected artifacts

<div className="craik-fields">

<div>
<dt>Artifact</dt>
<dt><span className="craik-fields__type">Kind</span></dt>
<dd>ID</dd>
</div>

<div>
<dt>Project</dt>
<dt><span className="craik-fields__type">deterministic</span></dt>
<dd><code>project_stigmem</code></dd>
</div>

<div>
<dt>Task</dt>
<dt><span className="craik-fields__type">deterministic</span></dt>
<dd><code>task_stigmem_documentation_reconciliation</code></dd>
</div>

<div>
<dt>Case file</dt>
<dt><span className="craik-fields__type">deterministic</span></dt>
<dd><code>case_stigmem_documentation_reconciliation</code></dd>
</div>

<div>
<dt>Receipt</dt>
<dt><span className="craik-fields__type">deterministic</span></dt>
<dd><code>receipt_demo_stigmem_documentation_reconciliation</code></dd>
</div>

<div>
<dt>Handoff</dt>
<dt><span className="craik-fields__type">deterministic</span></dt>
<dd><code>handoff_stigmem_documentation_reconciliation</code></dd>
</div>

<div>
<dt>Graph</dt>
<dt><span className="craik-fields__type">deterministic</span></dt>
<dd><code>graph_task_stigmem_documentation_reconciliation</code></dd>
</div>

<div>
<dt>Local memory proposal</dt>
<dt><span className="craik-fields__type">created</span></dt>
<dd>One.</dd>
</div>

<div>
<dt>Local contradiction report</dt>
<dt><span className="craik-fields__type">created</span></dt>
<dd>One.</dd>
</div>

<div>
<dt>Provider runs</dt>
<dt><span className="craik-fields__type">summary</span></dt>
<dd>OpenAI + Anthropic under <code>provider_executions</code>.</dd>
</div>

</div>

Inspect follow-up artifacts:

```sh
craik case show task_stigmem_documentation_reconciliation
craik contradictions list --task-id task_stigmem_documentation_reconciliation
craik memory list --task-id task_stigmem_documentation_reconciliation
craik handoff show task_stigmem_documentation_reconciliation
craik graph export --task-id task_stigmem_documentation_reconciliation
```

## Boundary behavior

<div className="craik-keypoint">

**ADRs and immutable paths are evidence.**

The demo never edits repository files. Proposed documentation updates
are emitted as reviewable suggestions in the JSON payload. Public docs
do not receive internal-only labels, private planning names, local
filesystem paths, or secrets.

</div>

## Memory behavior

The demo creates a local memory proposal. It does not write directly
to Stigmem because direct durable memory writes require explicit
policy grants. The JSON payload includes
`memory_write.status = "proposal_created"` so release acceptance can
verify the memory-write path remained explicit.

## Provider behavior

The demo exercises `provider_openai` and `provider_anthropic` through
the deterministic provider-backed runner. These runs normalize
provider payloads, record provider receipts, create run-scoped
handoffs, and do not require live OpenAI or Anthropic credentials.

## Expected output shape

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

<div className="craik-fields">

<div>
<dt>Symptom</dt>
<dt><span className="craik-fields__type">Cause</span></dt>
<dd>Fix</dd>
</div>

<div>
<dt><code>stigmem_backend_status.status = "not_configured"</code> or <code>"error"</code></dt>
<dt><span className="craik-fields__type">offline backend</span></dt>
<dd>Demo still runs — these statuses are informational, not blocking.</dd>
</div>

<div>
<dt>GitHub unavailable</dt>
<dt><span className="craik-fields__type">network</span></dt>
<dd>Use <code>--no-github</code>. The case file will include an open assumption or stale-risk warning that GitHub state was not loaded.</dd>
</div>

<div>
<dt>No ADRs discovered</dt>
<dt><span className="craik-fields__type">repo layout</span></dt>
<dd>Confirm the repository has <code>docs/adr/</code>, or pass project registration options.</dd>
</div>

<div>
<dt>Not a Git repository</dt>
<dt><span className="craik-fields__type">path</span></dt>
<dd>Pass <code>--repo-path</code> to a directory inside the Stigmem checkout.</dd>
</div>

</div>

## What's next

<div className="craik-next">

<a href="../quickstart/">
<strong>Guide</strong>
<span>Quickstart</span>
<small>The shorter introductory workflow.</small>
</a>

<a href="../connecting-stigmem/">
<strong>Guide</strong>
<span>Connecting Stigmem</span>
<small>Set up the optional live backend.</small>
</a>

<a href="../using-case-files/">
<strong>Guide</strong>
<span>Using case files</span>
<small>Read the case-file structure the demo produces.</small>
</a>

</div>
