# Human delegation and scope changes

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The two contracts that bound where autonomous agents must stop —
`craik.human_delegation_point` for delegated decisions and
`craik.scope_change_request` / `_result` for changes to accepted task
scope.

</div>

<div className="craik-keypoint">

**Open delegation blocks autonomy.**

Open delegation points and pending scope-change requests block
autonomous continuation. Resolutions must be durable and auditable.

</div>

## Delegation kinds

<div className="craik-fields">

<div>
<dt>Kind</dt>
<dt><span className="craik-fields__type">Use for</span></dt>
<dd>Trigger</dd>
</div>

<div>
<dt><code>approval</code></dt>
<dt><span className="craik-fields__type">authorization</span></dt>
<dd>Human authorization is required by policy or task boundary.</dd>
</div>

<div>
<dt><code>clarification</code></dt>
<dt><span className="craik-fields__type">ambiguity</span></dt>
<dd>The request is ambiguous enough that guessing would change behavior or scope.</dd>
</div>

<div>
<dt><code>escalation</code></dt>
<dt><span className="craik-fields__type">unresolved risk</span></dt>
<dd>An unresolved risk, contradiction, or policy issue needs a human decision.</dd>
</div>

<div>
<dt><code>ownership_transfer</code></dt>
<dt><span className="craik-fields__type">handover</span></dt>
<dd>The agent should transfer responsibility to a human or another owner before further work.</dd>
</div>

</div>

Resolved delegation points must include resolution text.

## Scope changes

<div className="craik-fields">

<div>
<dt>Contract</dt>
<dt><span className="craik-fields__type">Records</span></dt>
<dd>Lifecycle</dd>
</div>

<div>
<dt><code>craik.scope_change_request</code></dt>
<dt><span className="craik-fields__type">request</span></dt>
<dd>Current scope · proposed scope · reason · intent lock · optional policy envelope · contradictions · handoffs.</dd>
</div>

<div>
<dt><code>craik.scope_change_result</code></dt>
<dt><span className="craik-fields__type">decision</span></dt>
<dd>Records the human decision. Rejected changes keep the existing scope. Accepted changes must link to an updated intent lock so the new boundary is durable and auditable.</dd>
</div>

</div>

## Handoffs

Handoffs surface `open_human_delegation_ids`,
`scope_change_request_ids`, and `scope_change_result_ids`. A blocked
handoff must list open delegation points and explain what human input
is required before work resumes.

## What's next

<div className="craik-next">

<a href="../delegation-queue-view/">
<strong>Reference</strong>
<span>Delegation queue view</span>
<small>The operator surface that displays open delegations.</small>
</a>

<a href="../schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The full delegation and scope-change schemas.</small>
</a>

<a href="../../guides/scope-control/">
<strong>Guide</strong>
<span>Scope control</span>
<small>How intent locks and stop-conditions compose with delegation.</small>
</a>

</div>
