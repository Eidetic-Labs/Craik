# Provider budgets

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The pre-routing budget and quota check that gates whether Craik is
allowed to dispatch a request to a configured model provider. This is
the gate; the [budget and quota view](../budget-quota-view/) is the
read-only operator display of the same information.

</div>

<div className="craik-keypoint">

**References only, never secrets.**

Status records carry `budget_ref` and `quota_ref` strings that point at
external budget and quota systems. Concrete amounts, account ids, and
credentials never enter the routing decision payload.

</div>

## Records

<div className="craik-grid">

<div><h4><code>ProviderBudgetStatus</code></h4></div>
<div><h4><code>ProviderRoutingBudgetDecision</code></h4></div>

</div>

### `ProviderBudgetStatus`

Non-secret budget and quota snapshot for one provider, prepared by the
operator surface or an integration before routing is attempted.

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Meaning</dd>
</div>

<div>
<dt><code>provider_id</code></dt>
<dt><span className="craik-fields__type">str</span></dt>
<dd>The provider the status applies to. Must match the routed provider.</dd>
</div>

<div>
<dt><code>budget_ref</code></dt>
<dt><span className="craik-fields__type">str | None</span></dt>
<dd>Reference to the external budget record. Not a value, not a secret.</dd>
</div>

<div>
<dt><code>quota_ref</code></dt>
<dt><span className="craik-fields__type">str | None</span></dt>
<dd>Reference to the external quota record.</dd>
</div>

<div>
<dt><code>budget_remaining</code></dt>
<dt><span className="craik-fields__type">float | None</span></dt>
<dd>Remaining budget in the integrating system's units. Optional; absence means unknown, not unlimited.</dd>
</div>

<div>
<dt><code>quota_remaining</code></dt>
<dt><span className="craik-fields__type">int | None</span></dt>
<dd>Remaining quota in calls or requests.</dd>
</div>

<div>
<dt><code>blocked</code></dt>
<dt><span className="craik-fields__type">bool</span></dt>
<dd>Explicit block flag set upstream (for example, by an admin freeze).</dd>
</div>

<div>
<dt><code>reason</code></dt>
<dt><span className="craik-fields__type">str | None</span></dt>
<dd>Human-readable rationale for a block. Surfaced verbatim in the decision.</dd>
</div>

</div>

### `ProviderRoutingBudgetDecision`

The structured allow-or-deny outcome produced by
`provider_budget_decision(provider, status)` and consumed by the
provider router.

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Meaning</dd>
</div>

<div>
<dt><code>allowed</code></dt>
<dt><span className="craik-fields__type">bool</span></dt>
<dd>Whether routing is permitted under the current status.</dd>
</div>

<div>
<dt><code>provider_id</code></dt>
<dt><span className="craik-fields__type">str</span></dt>
<dd>The provider the decision applies to.</dd>
</div>

<div>
<dt><code>reason</code></dt>
<dt><span className="craik-fields__type">str</span></dt>
<dd>Why the decision came out the way it did. Always populated.</dd>
</div>

<div>
<dt><code>budget_ref</code> · <code>quota_ref</code></dt>
<dt><span className="craik-fields__type">str | None</span></dt>
<dd>Carried through from the provider record so receipts can trace the decision back to its source.</dd>
</div>

<div>
<dt><code>budget_remaining</code> · <code>quota_remaining</code></dt>
<dt><span className="craik-fields__type">float | None · int | None</span></dt>
<dd>The remainders observed at decision time. Only present on allow decisions or when surfaced by an explicit block reason.</dd>
</div>

</div>

## Decision rules

<div className="craik-keypoint">

**A decision is always produced — never silently dropped.**

`provider_budget_decision` returns a `ProviderRoutingBudgetDecision` in
every case. The provider router is expected to read `allowed` and
`reason` directly; there is no second channel for "no answer."

</div>

The check denies routing when any of the following is true, in order:

<div className="craik-grid">

<div><h4>Status mismatch</h4><p><code>status.provider_id</code> does not equal the provider being routed.</p></div>
<div><h4>Explicit block</h4><p><code>status.blocked</code> is set. The status <code>reason</code> is surfaced verbatim; absent reason falls back to "provider budget status is blocked."</p></div>
<div><h4>Budget exhausted</h4><p><code>budget_remaining</code> is set and <code>&lt;= 0</code>.</p></div>
<div><h4>Quota exhausted</h4><p><code>quota_remaining</code> is set and <code>&lt;= 0</code>.</p></div>

</div>

Otherwise the decision is allowed with reason "provider budget and
quota allow routing."

<div className="craik-keypoint">

**Absent remainders mean unknown, not unlimited.**

`budget_remaining=None` and `quota_remaining=None` are treated as "no
signal" — the check does not block on them, but it also does not invent
a remaining amount. Integrations that want hard limits must populate
the value.

</div>

## What's next

<div className="craik-next">

<a href="../budget-quota-view/">
<strong>Reference</strong>
<span>Budget and quota view</span>
<small>The operator-surface display that visualizes status and decisions.</small>
</a>

<a href="../model-providers/">
<strong>Reference</strong>
<span>Model providers</span>
<small>How providers are configured and what fields the routing layer reads.</small>
</a>

<a href="../../concepts/governance/">
<strong>Read</strong>
<span>Governance</span>
<small>Why budget refs are first-class governance inputs, not afterthoughts.</small>
</a>

</div>
