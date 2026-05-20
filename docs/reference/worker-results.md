# Worker results

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `craik.worker_result` contract for multi-agent coordination —
how role-specific specialist outputs stay typed and reviewable
without flattening into consensus.

</div>

<div className="craik-keypoint">

**Don't flatten conflict.**

Specialist outputs stay typed even when agents disagree. Don't flatten
conflicting results into a single consensus — preserve contradictions
and let review or adjudication decide.

</div>

## Status

One of: `completed` · `blocked` · `failed` · `partial`.

## What it contains

<div className="craik-grid">

<div><h4>Structured findings</h4><p>Severity · evidence · artifact refs · contradiction ids.</p></div>
<div><h4>Artifacts</h4></div>
<div><h4>Assumptions</h4></div>
<div><h4>Risks</h4></div>
<div><h4>Proposed actions</h4></div>
<div><h4>Top-level contradiction ids</h4></div>
<div><h4>Evidence references</h4></div>
<div><h4>Receipt ids</h4></div>
<div><h4>Diagnostics</h4></div>
<div><h4>Redaction state</h4></div>

</div>

## Read-only investigations

<div className="craik-keypoint">

**Bounded by case file and policy.**

<code>ReadOnlyInvestigationOrchestrator</code> creates bounded
investigation requests for specialist roles and persists each
returned <code>craik.worker_result</code>. The helper requires a case
file, links requests to the active policy envelope, writes
read-only investigation receipts, and blocks work when policy does
not allow <code>repo.read</code> or <code>memory.read</code>.

</div>

Fixture investigations use `FixtureInvestigationSpecialist` for
deterministic local tests. Live specialists follow the same boundary:
read context, return typed findings, avoid side effects.

## What's next

<div className="craik-next">

<a href="../agent-roles/">
<strong>Reference</strong>
<span>Agent roles</span>
<small>The role kinds that produce worker results.</small>
</a>

<a href="../cross-agent-review/">
<strong>Reference</strong>
<span>Cross-agent review</span>
<small>How worker results get reviewed and adjudicated.</small>
</a>

<a href="../schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The <code>worker_result</code> shape.</small>
</a>

</div>
