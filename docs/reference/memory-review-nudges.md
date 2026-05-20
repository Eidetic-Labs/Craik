# Memory review nudges

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

How Craik identifies facts that should be reviewed — without directly
rewriting memory. The `MemoryReviewCandidate` record and the
`memory_review_nudge` helper.

</div>

<div className="craik-keypoint">

**Reminders, not writes.**

Review nudges do not alter facts, resolve contradictions, or promote
inferred preferences.

</div>

## Candidate record

`MemoryReviewCandidate`:

<div className="craik-grid">

<div><h4>Fact reference</h4></div>
<div><h4>Entity and relation</h4></div>
<div><h4>Scope</h4></div>
<div><h4>Confidence</h4></div>
<div><h4>Evidence ids</h4></div>
<div><h4>Last review timestamp</h4></div>
<div><h4>Optional expiry timestamp</h4></div>
<div><h4>Owner</h4></div>

</div>

## Nudge outcomes

`memory_review_nudge` returns either `not_due` or `due`. Due nudges
can be triggered by:

<div className="craik-grid">

<div><h4>Stale review cadence</h4></div>
<div><h4>Expired or expiring facts</h4></div>
<div><h4>Low confidence</h4></div>
<div><h4>Missing evidence</h4></div>

</div>

<div className="craik-keypoint">

**Due nudges require receipt ids.**

They preserve evidence and owner links so a reviewer can decide
whether to approve, reject, refresh, or invalidate the underlying fact
through the normal memory proposal workflow.

</div>

## What's next

<div className="craik-next">

<a href="../preference-facts/">
<strong>Reference</strong>
<span>Preference facts</span>
<small>Inferred preferences awaiting review.</small>
</a>

<a href="../../guides/memory-proposals/">
<strong>Guide</strong>
<span>Memory proposals</span>
<small>The proposal workflow review uses.</small>
</a>

<a href="../learning-receipts/">
<strong>Reference</strong>
<span>Learning receipts</span>
<small>The receipt subtype for learning-loop decisions.</small>
</a>

</div>
