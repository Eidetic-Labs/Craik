# Tool attestations and freshness

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

Two related contracts that bound the trust on observed tool results
and the recency of knowledge — `craik.tool_result_attestation` and
`craik.knowledge_freshness_probe`.

</div>

<div className="craik-keypoint">

**Recency, not truth.**

Freshness probes only record whether the expected source was observed
recently enough for the caller's freshness policy. They do not prove
the underlying claim is true.

</div>

## Contracts

<div className="craik-fields">

<div>
<dt>Contract</dt>
<dt><span className="craik-fields__type">Records</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>craik.tool_result_attestation</code></dt>
<dt><span className="craik-fields__type">tool output</span></dt>
<dd>Tool name &amp; identity · command when available · observed output summary · trust class · evidence/receipt links · capture time · optional expiry.</dd>
</div>

<div>
<dt><code>craik.knowledge_freshness_probe</code></dt>
<dt><span className="craik-fields__type">recency</span></dt>
<dd>Links a target (GitHub state · documentation · memory facts · tool results · external state · instruction sources) to freshness status and stale-risk warning text.</dd>
</div>

</div>

## Stale-risk surfaces

<div className="craik-keypoint">

**Surface expiring / expired / missing probes.**

Before a handoff or memory promotion relies on a piece of knowledge,
expiring, expired, and missing probes must surface as stale-risk
warnings.

</div>

## What's next

<div className="craik-next">

<a href="../known-traps/">
<strong>Reference</strong>
<span>Known traps</span>
<small>How freshness interacts with active traps.</small>
</a>

<a href="../schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>Full attestation and probe shapes.</small>
</a>

<a href="../../guides/agent-onboarding/">
<strong>Guide</strong>
<span>Agent onboarding</span>
<small>Where stale-risk warnings appear at run start.</small>
</a>

</div>
