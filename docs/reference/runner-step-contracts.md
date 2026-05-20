# Runner step contracts

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The two contracts that bound one phase of the single-agent execution
loop — `craik.runner_step_request` and `craik.runner_step_result`.

</div>

<div className="craik-keypoint">

**Authority stays explicit.**

The policy envelope and intent lock remain explicit so a runner step
cannot float away from the authority and scope that produced it.

</div>

## Step requests

`craik.runner_step_request` contains:

<div className="craik-grid">

<div><h4><code>run_id</code> &amp; <code>task_id</code></h4></div>
<div><h4>Loop <code>phase</code></h4></div>
<div><h4>Stable <code>runner</code> metadata</h4></div>
<div><h4><code>policy_envelope_id</code></h4><p>And optional <code>intent_lock_id</code>.</p></div>
<div><h4>Capability grants</h4><p>And expected output schemas.</p></div>
<div><h4><code>input_prompt</code></h4></div>
<div><h4>Bounded <code>context</code></h4></div>
<div><h4><code>redaction_required</code></h4></div>

</div>

## Step results

`craik.runner_step_result` contains:

<div className="craik-grid">

<div><h4>Originating <code>request_id</code></h4></div>
<div><h4>Same <code>run_id</code> · <code>task_id</code> · <code>phase</code> · <code>runner</code> metadata</h4></div>
<div><h4>Status</h4><p><code>completed</code> · <code>blocked</code> · <code>failed</code> · <code>partial</code>.</p></div>
<div><h4>Human-readable summary</h4></div>
<div><h4>Structured <code>observed_output</code></h4></div>
<div><h4>Diagnostics</h4></div>
<div><h4>Receipt ids</h4></div>
<div><h4>Memory proposal ids</h4></div>
<div><h4>Artifacts</h4></div>
<div><h4><code>redacted</code> flag</h4></div>

</div>

<div className="craik-keypoint">

**Contracts, not authority.**

Provider-specific details belong under structured output fields and
must remain redacted before persistence or handoff. Step contracts do
not grant authority, perform side effects, or decide continuation —
the loop executor will consume them with policy checks and task-run
state.

</div>

## What's next

<div className="craik-next">

<a href="../run-state/">
<strong>Reference</strong>
<span>Run state</span>
<small>The lifecycle that consumes these step contracts.</small>
</a>

<a href="../../concepts/single-agent-loop/">
<strong>Concept</strong>
<span>Single-agent loop</span>
<small>The phase model behind the contracts.</small>
</a>

<a href="../runner-adapter-contract/">
<strong>Reference</strong>
<span>Runner adapter contract</span>
<small>The runner-level surface that emits step requests.</small>
</a>

</div>
