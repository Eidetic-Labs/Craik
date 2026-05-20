# Skill telemetry

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

`SkillPerformanceTelemetry` — how one skill invocation behaved
without allowing the agent to silently rewrite reusable guidance.

</div>

<div className="craik-keypoint">

**Evidence for learning, not authority.**

Use telemetry as evidence for later proposals and promotion gates.
It does not change a skill on its own.

</div>

## Fields

<div className="craik-grid">

<div><h4>Telemetry id</h4></div>
<div><h4>Task id</h4></div>
<div><h4>Skill package id</h4></div>
<div><h4>Skill invocation context id</h4></div>
<div><h4>Outcome</h4><p><code>succeeded</code> · <code>failed</code> · <code>partial</code>.</p></div>
<div><h4>Duration (ms)</h4></div>
<div><h4>Validation signals</h4></div>
<div><h4>Evidence ids</h4></div>
<div><h4>Receipt ids</h4></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Redacted metadata</h4></div>
<div><h4>Creation timestamp</h4></div>

</div>

<div className="craik-keypoint">

**Failed telemetry requires at least one failed validation signal.**

All telemetry requires policy and receipt links.

</div>

## Redaction

<div className="craik-keypoint">

**Never persist raw payloads.**

Telemetry metadata must not persist raw prompts, inputs, outputs,
traces, stdout, stderr, raw errors, responses, payloads, credentials,
tokens, passwords, or API keys.

</div>

## What's next

<div className="craik-next">

<a href="skill-proposals/">
<strong>Reference</strong>
<span>Skill proposals</span>
<small>Draft reviewable changes from telemetry.</small>
</a>

<a href="learning-receipts/">
<strong>Reference</strong>
<span>Learning receipts</span>
<small>Record every learning decision.</small>
</a>

<a href="../guides/learning-loops/">
<strong>Guide</strong>
<span>Learning loops</span>
<small>The full discipline telemetry sits inside.</small>
</a>

</div>
