# ADR 0004 · Policy envelope shape

<p className="craik-meta"><span>2 min read</span><span>Accepted</span><span>Recorded 2026-05-01</span></p>

<div className="craik-lead">

**What this ADR decides**

That `craik.policy_envelope` is the stable governance boundary for a
task-scoped action context. Capability grants are kept as separate
records so they can be linked, expired, denied, or carried into
receipts independently.

</div>

<div className="craik-keypoint">

**Status: Accepted.**

Policy lives in artifacts, not in code paths. Every action threads a
policy envelope id and (where applicable) grant ids.

</div>

## Context

Craik coordinates agent work across file changes, shell commands,
provider calls, memory writes, handoffs, channel ingress, and sandbox
backends. Each action needs a stable record of actor, task, profile,
grant requirements, redaction posture, and receipt obligations.

## Decision

<div className="craik-fields">

<div>
<dt>Component</dt>
<dt><span className="craik-fields__type">Role</span></dt>
<dd>What it records</dd>
</div>

<div>
<dt><code>craik.policy_envelope</code></dt>
<dt><span className="craik-fields__type">envelope</span></dt>
<dd>Policy profile · actor · task id · allowed capabilities · fail-open posture · receipt requirements · handoff requirements · redaction requirements.</dd>
</div>

<div>
<dt>Capability grant</dt>
<dt><span className="craik-fields__type">separate record</span></dt>
<dd>Linked to the envelope · can be expired, denied, or carried into receipts independently.</dd>
</div>

<div>
<dt>Side-effect surfaces</dt>
<dt><span className="craik-fields__type">enforcement</span></dt>
<dd>Provider loops · side-effect wrappers · channels · sandboxes · memory workflows must check the envelope and grants before executing.</dd>
</div>

</div>

## Consequences

Policy behavior is explicit in artifacts rather than implicit in code
paths. This makes receipts and handoffs auditable. The cost is that
every new surface must thread policy envelope ids and grant ids
through its contracts.

## Alternatives considered

<div className="craik-fields">

<div>
<dt>Alternative</dt>
<dt><span className="craik-fields__type">Disposition</span></dt>
<dd>Why rejected</dd>
</div>

<div>
<dt>Embed policy decisions in task records</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>Policy can vary by actor and action; embedding it in tasks would conflate the two.</dd>
</div>

<div>
<dt>Runtime exceptions only</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>Would not produce durable evidence for reviewers or future agents.</dd>
</div>

</div>

<div className="craik-keypoint">

**Retraction: none active.**

Retract this ADR if Craik replaces policy envelopes with a formally
versioned external authorization service and migration path.

</div>

## What's next

<div className="craik-next">

<a href="../../reference/policy-profiles/">
<strong>Reference</strong>
<span>Policy profiles</span>
<small>Strict · trusted-local · automation — the shipped profiles.</small>
</a>

<a href="../../reference/policy-tests/">
<strong>Reference</strong>
<span>Policy tests</span>
<small>The regression harness that keeps envelopes honest.</small>
</a>

<a href="../receipts-and-handoffs-as-public-contracts/">
<strong>ADR</strong>
<span>0005 · Receipts and handoffs as public contracts</span>
<small>Why every envelope decision produces durable evidence.</small>
</a>

</div>
