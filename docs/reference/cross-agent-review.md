# Cross-agent review

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

How one specialist role requests review from another without
collapsing distinct decisions into a single worker result.

</div>

<div className="craik-keypoint">

**Reviewers cite; they don't rewrite.**

Reviewers can cite evidence, contradictions, receipts, handoffs,
worker results, and debate summaries. They do not rewrite worker
output in place — revisions are recorded as adjudicated findings with
replacement text.

</div>

## Review flow

<ol className="craik-steps">
<li>Create <code>craik.review_request</code> for one or more worker results or debate summaries.</li>
<li>The reviewer returns <code>craik.review_result</code> with a decision of <code>approved</code>, <code>changes_requested</code>, <code>blocked</code>, or <code>deferred</code>.</li>
<li>An adjudicator records <code>craik.adjudication_outcome</code> with a decision of <code>accepted</code>, <code>rejected</code>, <code>revised</code>, or <code>deferred</code>.</li>
<li>Handoffs include <code>adjudication_ids</code> and <code>unresolved_disagreements</code> so the next agent can resume from the durable decision boundary.</li>
</ol>

## Reviewer boundaries

<div className="craik-keypoint">

**Distinct roles stay explicit.**

Policy reviewer and adversarial reviewer results remain separate.
Adjudication outcomes preserve <code>policy_review_result_ids</code>
and <code>adversarial_review_result_ids</code> so later agents can see
which role made each decision.

</div>

## Deferral

<div className="craik-fields">

<div>
<dt>Outcome</dt>
<dt><span className="craik-fields__type">Use for</span></dt>
<dd>Required state</dd>
</div>

<div>
<dt><code>deferred</code></dt>
<dt><span className="craik-fields__type">durable</span></dt>
<dd>Requires at least one unresolved disagreement and must be carried into the next handoff. Use when the adjudicator cannot accept, reject, or revise without more context, human review, or a policy decision.</dd>
</div>

</div>

## What's next

<div className="craik-next">

<a href="agent-roles/">
<strong>Reference</strong>
<span>Agent roles</span>
<small>The role kinds that request and produce reviews.</small>
</a>

<a href="debates/">
<strong>Reference</strong>
<span>Structured debates</span>
<small>The debate record adjudication consumes.</small>
</a>

<a href="schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The <code>review_request</code> / <code>review_result</code> / <code>adjudication_outcome</code> shapes.</small>
</a>

</div>
