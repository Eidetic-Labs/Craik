# Skill proposals

<p className="craik-meta"><span>3 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

`SkillChangeProposal` — how agents draft changes to reusable
operating guidance without silently changing their own authority.

</div>

<div className="craik-keypoint">

**Proposals are not updates.**

Reviewable records that can be cited by later approval gates, eval /
replay checks, rollback plans, and learning-loop receipts.

</div>

## Fields

<div className="craik-grid">

<div><h4>Proposal id</h4></div>
<div><h4>Skill package id</h4></div>
<div><h4>Task id</h4></div>
<div><h4>Title · summary · rationale · proposed change</h4></div>
<div><h4>Source</h4><p><code>telemetry</code> · <code>operator</code> · <code>review</code>.</p></div>
<div><h4>Status</h4><p><code>pending_review</code> · <code>approved</code> · <code>rejected</code>.</p></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Evidence ids</h4></div>
<div><h4>Telemetry ids</h4></div>
<div><h4>Receipt ids</h4></div>
<div><h4>Optional improvement plan</h4></div>
<div><h4>Creator &amp; creation timestamp</h4></div>

</div>

<div className="craik-keypoint">

**Agent-created proposals stay <code>pending_review</code>.**

Review and promotion are separate gates. Telemetry-sourced proposals
require telemetry ids so reviewers can inspect the observed behavior
that motivated the change.

</div>

## Improvement plans

`SkillImprovementPlan` adds structured review details:

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Values</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt>Expected benefit</dt>
<dt><span className="craik-fields__type">prose</span></dt>
<dd>What improvement to expect.</dd>
</div>

<div>
<dt>Risk</dt>
<dt><span className="craik-fields__type"><code>low</code> / <code>medium</code> / <code>high</code> / <code>critical</code></span></dt>
<dd>High &amp; critical require replay fixture ids.</dd>
</div>

<div>
<dt>Rollback notes</dt>
<dt><span className="craik-fields__type">prose</span></dt>
<dd>The path back.</dd>
</div>

<div>
<dt>Proposed edit targets</dt>
<dt><span className="craik-fields__type">list</span></dt>
<dd>Where the change applies.</dd>
</div>

<div>
<dt>Replay fixture ids</dt>
<dt><span className="craik-fields__type">list</span></dt>
<dd>Required for high / critical risk.</dd>
</div>

</div>

<div className="craik-keypoint">

**Approved proposals require an improvement plan.**

Reviewers must inspect benefit, risk, edit scope, and rollback path
before promotion.

</div>

## What's next

<div className="craik-next">

<a href="skill-promotion-gates/">
<strong>Reference</strong>
<span>Skill promotion gates</span>
<small>Turn an approved proposal into promoted guidance.</small>
</a>

<a href="skill-replay/">
<strong>Reference</strong>
<span>Skill replay</span>
<small>Compare current behavior against fixtures before promotion.</small>
</a>

<a href="skill-rollbacks/">
<strong>Reference</strong>
<span>Skill rollbacks</span>
<small>The reviewable path back to a prior promoted version.</small>
</a>

</div>
