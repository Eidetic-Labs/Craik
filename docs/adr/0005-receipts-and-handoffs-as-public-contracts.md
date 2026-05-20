# ADR 0005 · Receipts and handoffs as public contracts

<p className="craik-meta"><span>2 min read</span><span>Accepted</span><span>Recorded 2026-05-01</span></p>

<div className="craik-lead">

**What this ADR decides**

That capability receipts and handoffs are public Craik contracts —
schema-validated, redacted before persistence, linked to policy
envelopes, and safe to cite from docs, operator views, work graphs,
and recovery flows.

</div>

<div className="craik-keypoint">

**Status: Accepted.**

Logs are not durable evidence. Every side-effect surface must emit or
link a receipt.

</div>

## Context

Craik's value depends on durable agent work: future agents and
operators need to know what happened, why it was allowed, what
evidence was used, and what remains unresolved. Receipts and handoffs
therefore sit at the boundary between runtime execution, memory, docs,
and operator workflows.

## Decision

<div className="craik-decision">

<div>
<h4>Capability receipts</h4>
<p>Record capability decisions and outcomes · schema-validated · redacted before persistence · linked to policy envelopes where available.</p>
</div>

<div>
<h4>Handoffs</h4>
<p>Summarize run state · completed actions · validation · risks · context debt · next steps · self-audit. Incomplete or blocked runs still produce handoffs when enough context is available.</p>
</div>

</div>

<div className="craik-keypoint">

**Evidence by reference, not copy.**

Receipts and handoffs link evidence by id rather than copying private
payloads — keeps them small and safe to cite without leaking content.

</div>

## Consequences

The runtime can recover from interruptions and preserve accountability
across agent boundaries. The cost is that every new side-effect
surface must emit or link receipts instead of treating logs as
sufficient evidence.

## Alternatives considered

<div className="craik-fields">

<div>
<dt>Alternative</dt>
<dt><span className="craik-fields__type">Disposition</span></dt>
<dd>Why rejected</dd>
</div>

<div>
<dt>Plain-text logs</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>Difficult to validate, redact, and query.</dd>
</div>

<div>
<dt>Optional prose handoffs</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>Breaks resume, review, and cross-agent continuity.</dd>
</div>

</div>

<div className="craik-keypoint">

**Retraction: none active.**

Retract this ADR if Craik replaces receipts and handoffs with another
versioned audit object and provides compatibility exports.

</div>

## What's next

<div className="craik-next">

<a href="../../runtime-contracts/">
<strong>Read</strong>
<span>Runtime contracts</span>
<small>The shipped receipt and handoff schemas.</small>
</a>

<a href="../policy-envelope-shape/">
<strong>ADR</strong>
<span>0004 · Policy envelope shape</span>
<small>The governance boundary receipts and handoffs link to.</small>
</a>

<a href="../../reference/handoff-viewer/">
<strong>Reference</strong>
<span>Handoff viewer</span>
<small>The operator surface backed by this contract.</small>
</a>

</div>
