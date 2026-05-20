# Learning receipts

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The capability-receipt subtype used for self-improvement decisions —
which actions it covers, the linked context, and the redaction floor.

</div>

<div className="craik-keypoint">

**Records decisions, doesn't make them.**

Learning receipts record decisions. They do not approve promotion,
rewrite skills, write memory facts, or export trajectories by
themselves.

</div>

## Supported actions

<div className="craik-grid">

<div><h4><code>proposal</code></h4></div>
<div><h4><code>review</code></h4></div>
<div><h4><code>eval_replay</code></h4></div>
<div><h4><code>promotion</code></h4></div>
<div><h4><code>rollback</code></h4></div>
<div><h4><code>export</code></h4></div>

</div>

## Linked context

`LearningReceiptContext` links receipts to:

<div className="craik-grid">

<div><h4>Task</h4></div>
<div><h4>Policy</h4></div>
<div><h4>Skill package</h4></div>
<div><h4>Proposal</h4></div>
<div><h4>Telemetry</h4></div>
<div><h4>Replay fixture</h4></div>
<div><h4>Preference</h4></div>
<div><h4>Memory fact</h4></div>
<div><h4>Evidence</h4></div>
<div><h4>Prior receipt context</h4></div>

</div>

## Redaction

<div className="craik-keypoint">

**Ids and summaries, not raw training examples.**

Learning receipts redact trajectories, raw trajectories, prompts,
responses, conversation payloads, export payloads, preference
evidence, credentials, and secret-like metadata keys.

</div>

## What's next

<div className="craik-next">

<a href="trajectory-exports/">
<strong>Reference</strong>
<span>Trajectory exports</span>
<small>The redacted replay-and-review artifact.</small>
</a>

<a href="skill-promotion-gates/">
<strong>Reference</strong>
<span>Skill promotion gates</span>
<small>The gates a learning receipt records.</small>
</a>

<a href="../guides/learning-loops/">
<strong>Guide</strong>
<span>Learning loops</span>
<small>The full discipline.</small>
</a>

</div>
