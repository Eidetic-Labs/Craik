# Memory Proposals

<p className="craik-meta"><span>5 min read</span><span>For runners &amp; reviewers</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Create, list, approve, and reject memory proposals — the default path for
any agent-initiated memory update in Craik. By the end you'll know the
full proposal lifecycle, the promotion rule that gates approval, and how
run outputs feed proposals during execution.

</div>

<div className="craik-keypoint">

**Proposal-first**

Craik defaults to **reviewable memory proposals** instead of direct
durable writes. Proposals require evidence, remain visible for audit
whether approved or rejected, and never become durable facts until a
reviewer (or a `memory.write` grant) promotes them.

</div>

## The lifecycle in one diagram

```text
agent or human ──propose──▶ memory_proposal (pending)
                                  │
                                  ├── reviewer approves ─▶ fact (local)
                                  ├── reviewer rejects  ─▶ stays for audit
                                  └── promotion expires ─▶ stays pending
```

## 1 · Create a proposal

```bash title="A proposal with explicit evidence"
craik memory propose task_review_docs \
  --entity repo:example \
  --relation craik:current_state \
  --value "Local proposals require review." \
  --source README.md \
  --evidence-source README.md \
  --evidence-locator README.md#memory \
  --evidence-summary "README documents local proposal behavior."
```

The flags map directly to a `craik.memory_proposal` record:

<div className="craik-fields">

<div>
<dt>Flag</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>--entity</code></dt>
<dt><span className="craik-fields__type">entity_uri</span></dt>
<dd>The subject of the fact: <code>repo:example</code>, <code>project:product</code>, etc.</dd>
</div>

<div>
<dt><code>--relation</code></dt>
<dt><span className="craik-fields__type">relation_name</span></dt>
<dd>The predicate, namespaced: <code>craik:current_state</code>, <code>product:owner</code>.</dd>
</div>

<div>
<dt><code>--value</code></dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>The object of the fact, in plain language.</dd>
</div>

<div>
<dt><code>--source</code></dt>
<dt><span className="craik-fields__type">uri</span></dt>
<dd>Where the proposal originated — file, URL, fact id.</dd>
</div>

<div>
<dt><code>--evidence-source</code> / <code>--evidence-locator</code> / <code>--evidence-summary</code></dt>
<dt><span className="craik-fields__type">evidence_reference</span></dt>
<dd>The evidence reference that supports the proposal. Required for promotion.</dd>
</div>

</div>

## 2 · List and filter

```bash title="Proposals for a task"
craik memory list --task-id task_review_docs
```

```bash title="All pending proposals"
craik memory list --status pending
```

## 3 · Approve or reject

```bash title="Approve with reasoning"
craik memory approve memprop_review_docs_repo_example_craik_current_state \
  --decided-by user:reviewer \
  --reason "Evidence supports the proposal."
```

```bash title="Reject with reasoning"
craik memory reject memprop_review_docs_repo_example_craik_current_state \
  --decided-by user:reviewer \
  --reason "Too broad for durable memory."
```

Both decisions are durable. Rejected proposals remain queryable for
audit — you can answer "did we ever consider this fact and why did we
reject it?" months later.

## 4 · Search approved facts

```bash title="Search promoted facts"
craik memory search "local proposals"
```

Pending and rejected proposals are **not** returned as facts. They remain
in local state for audit and later review, but the fact-search path only
sees what's been promoted.

## The promotion rule

<div className="craik-keypoint">

**Promotion requires evidence.**

A proposal without an evidence reference cannot be approved. Period. The
runtime refuses to promote it.

</div>

This is the single most important invariant in the memory system. Break
it, and downstream case files start inheriting unverifiable facts. Keep
it, and every approved fact in memory can be traced back to source
material a reviewer signed off on.

## Direct writes need a separate path

Direct durable writes still require a matching `memory.write` policy grant.
Until that grant exists, even runs operating under broad capability
postures must use proposals.

Without `memory.write`:

<ol className="craik-steps">
<li>The runtime creates a proposal instead of writing.</li>
<li>The proposal references the run that produced it.</li>
<li>A receipt is sealed naming the missing capability.</li>
<li>The reviewer flow decides whether to grant or to keep proposing.</li>
</ol>

This is the same pattern as every other capability — see
[Capability grants](capability-grants.md) for the full shape.

## Proposals during runs

Runner step observations are stored as `craik.run_output` records
**before** they become memory. A run output can create reviewable
proposals, but it cannot write durable facts directly.

Run-created proposals keep links to:

<div className="craik-grid">

<div>
<h4><code>run_id</code></h4>
<p>The run that produced the proposal.</p>
</div>

<div>
<h4><code>step_id</code></h4>
<p>The specific runner step inside the run.</p>
</div>

<div>
<h4><code>handoff_id</code></h4>
<p>The handoff that closed the run, when one exists.</p>
</div>

<div>
<h4>Evidence reference</h4>
<p>Points back to the run output and step result so reviewers can inspect what the runner actually observed.</p>
</div>

</div>

Blocked or failed step results are captured for inspection but **do not**
create memory proposals. Only completed and partial step results may
create proposals, and only when the executor supplies explicit proposal
specs. This stops a flailing run from contaminating the proposal queue.

## What's next

<div className="craik-next">

<a href="memory-impact-preview.md">
<strong>Do</strong>
<span>Preview impact before approving</span>
<small>See what a promotion would do to existing facts before saying yes.</small>
</a>

<a href="memory-diffs.md">
<strong>Do</strong>
<span>Memory diffs</span>
<small>Inspect the full memory delta a task produced.</small>
</a>

<a href="../concepts/memory-and-stigmem.md">
<strong>Read</strong>
<span>Memory &amp; Stigmem</span>
<small>The memory model and the Craik / Stigmem ownership split.</small>
</a>

</div>
