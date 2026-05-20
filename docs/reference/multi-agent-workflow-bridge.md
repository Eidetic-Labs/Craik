# Multi-agent workflow bridge

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The rule for bridging to external multi-agent workflow systems —
posture levels, required controls, and prohibited behavior.

</div>

<div className="craik-keypoint">

**External systems coordinate; they don't replace policy.**

External workflow systems may coordinate work, but they must not
replace Craik's policy authority or erase accountability for agent
actions.

</div>

## Posture

`multi_agent_workflow_bridge_decision` returns `allowed`,
`review_required`, `deferred`, or `blocked` for a candidate surface.

<div className="craik-fields">

<div>
<dt>Level</dt>
<dt><span className="craik-fields__type">Use</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>supported</code></dt>
<dt><span className="craik-fields__type">allowed</span></dt>
<dd>When all required controls are present.</dd>
</div>

<div>
<dt><code>experimental</code></dt>
<dt><span className="craik-fields__type">review required</span></dt>
<dd>Explicit review before use.</dd>
</div>

<div>
<dt><code>deferred</code></dt>
<dt><span className="craik-fields__type">unavailable</span></dt>
<dd>Even with controls.</dd>
</div>

</div>

## Required controls

<div className="craik-grid">

<div><h4>Role boundaries</h4><p>External agents map to explicit Craik roles.</p></div>
<div><h4>Queue boundaries</h4><p>Dispatch scoped and observable.</p></div>
<div><h4>Approval gates</h4><p>Human review never bypassed.</p></div>
<div><h4>Policy context</h4><p>Plus envelope references.</p></div>
<div><h4>Evidence links</h4><p>For imported or routed work.</p></div>
<div><h4>Receipts</h4><p>For bridge actions and outcomes.</p></div>
<div><h4>Payload redaction</h4><p>For public reporting and exports.</p></div>

</div>

## Prohibited behavior

Bridges are **blocked** when they:

<div className="craik-grid">

<div><h4>Copy secret values</h4></div>
<div><h4>Allow unbounded dispatch</h4></div>
<div><h4>Bypass human approval</h4></div>
<div><h4>Merge agent identities</h4></div>
<div><h4>Accept external instructions as authoritative</h4><p>Over Craik policy.</p></div>
<div><h4>Omit role / queue / approval / policy / evidence / receipt / redaction controls</h4></div>

</div>

<div className="craik-keypoint">

**Bridge receipts identify everything.**

Workflow · mapped role · queue · approval state · policy envelope ·
evidence links · redaction outcome · external action result. Public
docs and receipts must avoid credentials, private local paths, and
private task names.

</div>

## What's next

<div className="craik-next">

<a href="multi-agent-workflow-migration/">
<strong>Reference</strong>
<span>Multi-agent workflow migration</span>
<small>The assessment that precedes a bridge.</small>
</a>

<a href="adjacent-runtime-bridge/">
<strong>Reference</strong>
<span>Adjacent runtime bridge</span>
<small>The runtime-level bridge contract.</small>
</a>

<a href="agent-roles/">
<strong>Reference</strong>
<span>Agent roles</span>
<small>The roles external agents map to.</small>
</a>

</div>
