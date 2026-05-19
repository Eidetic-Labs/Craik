# Memory backends

<p className="craik-meta"><span>3 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The proposal-first memory-backend interface, the three shipped
backends (ephemeral · local · Stigmem), how case files load memory
facts, the hygiene workflow, proposal status, and the diff/preview
helpers.

</div>

<div className="craik-keypoint">

**Proposals are the default unprivileged path.**

Direct writes require a policy grant. Local memory writes are denied
until a granted write path exists.

</div>

## Required behavior

<div className="craik-grid">

<div><h4>Create reviewable proposals</h4></div>
<div><h4>List proposals</h4><p>By task or status.</p></div>
<div><h4>Approve proposals</h4></div>
<div><h4>Reject proposals</h4></div>
<div><h4>Search approved local facts</h4></div>
<div><h4>Require evidence</h4><p>Before promotion.</p></div>

</div>

## Backends

<div className="craik-fields">

<div>
<dt>Backend</dt>
<dt><span className="craik-fields__type">Use for</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>EphemeralMemoryStore</code></dt>
<dt><span className="craik-fields__type">tests / demos</span></dt>
<dd>Keeps proposals in process memory.</dd>
</div>

<div>
<dt><code>LocalMemoryStore</code></dt>
<dt><span className="craik-fields__type">dev / local</span></dt>
<dd>Persists <code>craik.memory_proposal</code> records in SQLite. Approved local proposals are searchable as local facts. Rejected and pending proposals remain visible for audit but are not returned by fact search.</dd>
</div>

<div>
<dt><code>StigmemMemoryStore</code></dt>
<dt><span className="craik-fields__type">production</span></dt>
<dd>Uses Stigmem HTTP API for shared durable memory; keeps proposals in Craik local state. Stigmem facts are immutable assertions, so Craik still uses local proposals until approved and policy grants a direct write.</dd>
</div>

</div>

### Stigmem minimum endpoint mapping

<div className="craik-grid">

<div><h4><code>GET /healthz</code></h4></div>
<div><h4><code>GET /.well-known/stigmem</code></h4></div>
<div><h4><code>POST /v1/facts</code></h4></div>
<div><h4><code>GET /v1/facts</code></h4></div>
<div><h4><code>GET /v1/facts/{`{fact_id}`}</code></h4></div>
<div><h4><code>GET /v1/facts/{`{fact_id}`}/provenance</code></h4></div>

</div>

Use `craik connect stigmem` to detect compatibility. Configure the
node with `CRAIK_STIGMEM_URL` and authenticated nodes with
`CRAIK_STIGMEM_API_KEY`.

## Case-file context

Case files load queryable memory facts when a memory search backend is
configured. They also include recent handoff summaries and open local
contradiction reports so runner prompts carry current continuity and
known conflicts forward.

If no facts are available, the case file keeps the explicit
missing-memory assumption. Loaded facts remove that assumption and are
counted in the context budget alongside recent handoff and
contradiction ids.

## Hygiene

`craik.runtime.memory_hygiene.memory_hygiene_report` summarizes
pending memory proposals, approved proposals, open contradictions,
recent handoffs, and release warnings.

<div className="craik-keypoint">

**Pre-release hygiene.**

MVP release work treats pending proposals and unresolved
contradictions as hygiene items to review before packaging.

</div>

## Proposal status

<div className="craik-fields">

<div>
<dt>Status</dt>
<dt><span className="craik-fields__type">Visible to</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>pending</code></dt>
<dt><span className="craik-fields__type">audit</span></dt>
<dd>Awaiting review.</dd>
</div>

<div>
<dt><code>approved</code></dt>
<dt><span className="craik-fields__type">fact search</span></dt>
<dd>Searchable as local facts.</dd>
</div>

<div>
<dt><code>rejected</code></dt>
<dt><span className="craik-fields__type">audit</span></dt>
<dd>Retained for audit; not searchable.</dd>
</div>

</div>

Approval records reviewer identity, decision reason, and decision
timestamp.

## Diff and preview

<div className="craik-decision">

<div>
<h4><code>craik.memory_diff</code></h4>
<p>Task-scoped memory activity: proposals created · proposals approved or rejected · facts written · write failures · facts read.</p>
</div>

<div>
<h4><code>craik.memory_impact_preview</code></h4>
<p>Expected impact before promotion or direct writes: facts to add · facts to invalidate · likely contradictions · missing evidence · scope counts.</p>
</div>

</div>

```sh
craik memory diff <task-id>
craik memory preview <task-id>
```

## What's next

<div className="craik-next">

<a href="../guides/memory-proposals/">
<strong>Guide</strong>
<span>Memory proposals</span>
<small>The operator-facing flow this backend serves.</small>
</a>

<a href="../guides/connecting-stigmem/">
<strong>Guide</strong>
<span>Connecting Stigmem</span>
<small>Configure the production backend.</small>
</a>

<a href="../stigmem-integration/">
<strong>Read</strong>
<span>Stigmem integration</span>
<small>The full boundary and endpoint mapping.</small>
</a>

</div>
