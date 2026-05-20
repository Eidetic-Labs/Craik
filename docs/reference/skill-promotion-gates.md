# Skill promotion gates

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The gates that prevent reviewed skill proposals from becoming promoted
guidance without explicit approval — `SkillPromotionRequest` and
`SkillPromotionDecision`.

</div>

<div className="craik-keypoint">

**Approver must not be an agent.**

The approver is explicit and never an agent identity. Missing gates
produce a denied decision with reviewable denial reasons.

</div>

## Request

`SkillPromotionRequest`:

<div className="craik-grid">

<div><h4>Proposal id</h4></div>
<div><h4>Skill package id</h4></div>
<div><h4>Promoted version id</h4></div>
<div><h4>Approver</h4></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Evidence ids</h4></div>
<div><h4>Eval result ids</h4></div>
<div><h4>Receipt ids</h4></div>
<div><h4>Approval receipt id</h4></div>

</div>

## Decision

`SkillPromotionDecision`:

<div className="craik-grid">

<div><h4>Request id</h4></div>
<div><h4>Proposal id</h4></div>
<div><h4>Skill package id</h4></div>
<div><h4>Decision status</h4><p><code>approved</code> · <code>denied</code>.</p></div>
<div><h4>Approver</h4></div>
<div><h4>Promoted version id</h4></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Evidence ids · eval result ids · receipt ids</h4></div>
<div><h4>Denial reasons</h4></div>

</div>

## Required gates

Promotion is approved only when **every** gate is satisfied.

<ol className="craik-steps">
<li>The request references the same proposal, skill package, and policy envelope as the proposal.</li>
<li>The proposal status is <code>approved</code>.</li>
<li>The proposal has a structured improvement plan.</li>
<li>The approver is explicit and not an agent identity.</li>
<li>Evidence ids are present.</li>
<li>Eval result ids are present.</li>
<li>Receipt ids are present.</li>
<li>An approval receipt id is present.</li>
</ol>

## What's next

<div className="craik-next">

<a href="../skill-proposals/">
<strong>Reference</strong>
<span>Skill proposals</span>
<small>The proposal contract these gates accept or deny.</small>
</a>

<a href="../skill-replay/">
<strong>Reference</strong>
<span>Skill replay</span>
<small>The replay results that compose with promotion.</small>
</a>

<a href="../learning-receipts/">
<strong>Reference</strong>
<span>Learning receipts</span>
<small>Record promotion decisions.</small>
</a>

</div>
