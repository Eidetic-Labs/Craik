# Skill rollbacks

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The reviewable path for reverting promoted skill updates when a
promoted version causes regressions or violates policy — target,
request, and decision contracts.

</div>

<div className="craik-keypoint">

**Rollbacks don't invent guidance.**

Rollbacks point at a prior promoted version. They do not invent
replacement guidance — that requires a new proposal.

</div>

## Target

`SkillRollbackTarget`:

<div className="craik-grid">

<div><h4>Skill package id</h4></div>
<div><h4>Promoted version id</h4></div>
<div><h4>Rollback version id</h4></div>
<div><h4>Promoted proposal id</h4></div>
<div><h4>Promoted receipt id</h4></div>

</div>

The rollback version must be distinct from the promoted version.

## Request

`SkillRollbackRequest`:

<div className="craik-grid">

<div><h4>Task id</h4></div>
<div><h4>Rollback target</h4></div>
<div><h4>Rollback reason</h4></div>
<div><h4>Rationale</h4></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Evidence ids</h4></div>
<div><h4>Receipt ids</h4></div>
<div><h4>Replay result ids</h4></div>
<div><h4>Requester &amp; request timestamp</h4></div>

</div>

Requests require policy, evidence, and receipt references so reviewers
can audit why the rollback was proposed.

## Decision gate

<div className="craik-keypoint">

**Replay context required.**

<code>decide_skill_rollback</code> approves a rollback only when the
request has replay-result context and the decision records its own
receipt. Missing replay context or a missing decision receipt produces
a denied <code>SkillRollbackDecision</code>.

</div>

<div className="craik-fields">

<div>
<dt>Decision</dt>
<dt><span className="craik-fields__type">Preserves</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt>Approved</dt>
<dt><span className="craik-fields__type">version + receipt</span></dt>
<dd>Rollback version id and decision receipt id.</dd>
</div>

<div>
<dt>Denied</dt>
<dt><span className="craik-fields__type">reasons</span></dt>
<dd>Explicit denial reasons.</dd>
</div>

</div>

## What's next

<div className="craik-next">

<a href="../skill-promotion-gates/">
<strong>Reference</strong>
<span>Skill promotion gates</span>
<small>The decision rollbacks undo.</small>
</a>

<a href="../skill-replay/">
<strong>Reference</strong>
<span>Skill replay</span>
<small>The replay result rollback decisions require.</small>
</a>

<a href="../learning-receipts/">
<strong>Reference</strong>
<span>Learning receipts</span>
<small>Record rollback decisions with the <code>rollback</code> action.</small>
</a>

</div>
