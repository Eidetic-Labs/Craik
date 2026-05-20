# Provider failover

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The explicit routing policy that controls when Craik falls back from
one provider to another — rules, stop conditions, denied paths, and
the receipt shape.

</div>

<div className="craik-keypoint">

**No implicit fallback.**

Craik only falls back when a <code>ProviderFailoverPolicy</code>
contains a matching rule. Failover decisions preserve the active
policy envelope id so routing changes tie back to the same governance
boundary.

</div>

## Rules

`ProviderFailoverRule` defines:

<div className="craik-grid">

<div><h4>Failed provider id</h4></div>
<div><h4>Fallback provider id</h4></div>
<div><h4>Audit reason</h4></div>
<div><h4>Receipt required?</h4></div>

</div>

If no rule matches the failed provider, failover is denied.

## Stop conditions

<div className="craik-keypoint">

**Checked before fallback rules.**

Policies can name failure reasons that stop failover entirely. This
keeps routing from crossing policy, trust, or capability boundaries
after a failure reason that requires operator review.

</div>

Stopped decisions do not name a fallback provider.

## Denied fallback paths

Policies can deny specific fallback provider ids — even when a rule
points to that provider. This lets an operator disable a provider for
budget, trust, capability, incident, or compliance reasons without
removing every rule that references it.

## Receipts

`ProviderFailoverDecision` records whether failover was `allowed`,
`denied`, or `stopped`. Decisions include:

<div className="craik-grid">

<div><h4>Failed provider id</h4></div>
<div><h4>Fallback provider id</h4><p>When one was evaluated.</p></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Decision reason</h4></div>
<div><h4>Receipt requirement</h4></div>

</div>

<div className="craik-keypoint">

**Metadata only.**

Provider failover does not contact providers, load secrets, or grant
execution authority by itself. It supplies routing metadata for the
caller to enforce alongside provider switching, budgets, quotas, and
policy envelopes.

</div>

## What's next

<div className="craik-next">

<a href="../provider-switching/">
<strong>Reference</strong>
<span>Provider switching</span>
<small>The CLI surface for operator-driven selection.</small>
</a>

<a href="../model-providers/">
<strong>Reference</strong>
<span>Model providers</span>
<small>The registry and budget gating.</small>
</a>

<a href="../environment-receipts/">
<strong>Reference</strong>
<span>Environment receipts</span>
<small>How failover decisions persist.</small>
</a>

</div>
