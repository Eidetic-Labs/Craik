# Single-Agent Execution Loop

<p className="craik-meta"><span>5 min read</span><span>Core concept</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- The six bounded phases that make up the v0.1 single-agent loop.
- The safety boundaries Craik checks before each step.
- How runner output becomes typed run output and (sometimes) memory proposals.
- The recovery contract a resuming agent must honor.

</div>

<div className="craik-keypoint">

**Single-agent execution loop**

The v0.1 contract that lets one runner work through a governed task
without depending on an untracked chat transcript. The runner does the
reasoning; Craik owns the durable boundary — run state, policy checks,
receipts, step outputs, memory proposals, and recovery context.

</div>

## Lifecycle

A run starts as a `craik.task_run` with status `pending` and phase `plan`.
The executor moves through bounded steps:

<div className="craik-fields">

<div>
<dt>Phase</dt>
<dt><span className="craik-fields__type">Status it produces</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>plan</code></dt>
<dt><span className="craik-fields__type">→ running</span></dt>
<dd>Decide the next bounded action under the intent lock.</dd>
</div>

<div>
<dt><code>act</code></dt>
<dt><span className="craik-fields__type">→ running</span></dt>
<dd>Perform an approved side effect or propose one.</dd>
</div>

<div>
<dt><code>observe</code></dt>
<dt><span className="craik-fields__type">→ running</span></dt>
<dd>Capture output, diagnostics, receipts, and artifacts.</dd>
</div>

<div>
<dt><code>evaluate</code></dt>
<dt><span className="craik-fields__type">→ running</span></dt>
<dd>Decide whether to stop, continue, block, or fail.</dd>
</div>

<div>
<dt><code>continue</code></dt>
<dt><span className="craik-fields__type">→ running</span></dt>
<dd>Advance to another bounded iteration when needed.</dd>
</div>

<div>
<dt><code>stop</code></dt>
<dt><span className="craik-fields__type">→ terminal</span></dt>
<dd>Finalize state, handoff, receipts, and recovery context.</dd>
</div>

</div>

Terminal statuses are `completed`, `blocked`, `failed`, and
`interrupted`. Interrupted runs preserve enough local state for
inspection and later recovery.

## Safety boundaries

Before each step, Craik enforces three checks. None of them are advisory —
violating any of them halts the loop.

<div className="craik-grid">

<div>
<h4>Intent lock</h4>
<p>If a step would trigger a configured stop condition, the run halts before
the runner receives another request.</p>
</div>

<div>
<h4>Capability grant</h4>
<p>Side effects (shell, file write, memory write) need a matching grant.
Denied side effects produce denial receipts and block the run.</p>
</div>

<div>
<h4>Iteration ceiling</h4>
<p><code>max_iterations</code> bounds the loop. Reaching the bound interrupts
the run instead of continuing indefinitely.</p>
</div>

</div>

## Outputs &amp; memory

Runner output is captured as a `craik.runner_step_result`, then persisted
as a redacted `craik.run_output`. Run outputs can create reviewable
`craik.memory_proposal` records — they cannot write durable facts
directly.

Run-created proposals link back to the run for audit:

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt>task_id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>The task this proposal came out of.</dd>
</div>

<div>
<dt>run_id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>The specific run inside the task.</dd>
</div>

<div>
<dt>step_result_id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>The runner step that produced the observation.</dd>
</div>

<div>
<dt>handoff_id</dt>
<dt><span className="craik-fields__type">id (optional)</span></dt>
<dd>The handoff that closed the run, when one exists.</dd>
</div>

<div>
<dt>evidence</dt>
<dt><span className="craik-fields__type">evidence_reference[]</span></dt>
<dd>Pointers back to the captured run output and step result.</dd>
</div>

</div>

Blocked and failed steps are still inspectable, but they do **not**
create memory proposals. Only completed and partial step results may
propose, and only when the executor supplies explicit proposal specs.

## Fixture vs live runners

<div className="craik-decision">

<div>
<h4>Fixture execution</h4>
<ul>
<li>Uses <code>FixtureStepRunner</code> and deterministic step statuses.</li>
<li>For local tests, docs, and executor contract checks.</li>
<li>No credentials, no external side effects, byte-stable.</li>
<li>What CI exercises on every PR.</li>
</ul>
</div>

<div>
<h4>Live runner execution</h4>
<ul>
<li>Uses adapter-specific boundaries (Codex / Claude / Gemini today).</li>
<li>Same loop contract applies — only the runner backend differs.</li>
<li>Provider-specific details stay under structured, redacted metadata.</li>
<li>May require stricter grants depending on capability surface.</li>
</ul>
</div>

</div>

## Recovery

Recovery starts by inspecting the persisted run, receipts, outputs,
memory proposals, and handoff. **Recovery must not replay side effects
blindly.** A recovered run re-checks policy, intent-lock stop
conditions, and iteration limits before issuing another step request.

## Handoffs at terminal

Run handoffs summarize the terminal outcome through the existing
`craik.handoff` contract. A run handoff should include:

<div className="craik-grid">

<div>
<h4>Run status</h4>
<p><code>completed / blocked / failed / interrupted</code> with the last
phase reached.</p>
</div>

<div>
<h4>Captured outputs</h4>
<p>Runner metadata and the step-result ids that produced durable artifacts.</p>
</div>

<div>
<h4>Receipt ids</h4>
<p>Provider, side-effect, memory, and policy receipts emitted during the run.</p>
</div>

<div>
<h4>Diagnostics &amp; risks</h4>
<p>Residual risks, recovery guidance, and any context debt left for the next
agent — no claiming work that did not complete.</p>
</div>

</div>

## What's next

<div className="craik-next">

<a href="case-files.md">
<strong>Read</strong>
<span>Case files</span>
<small>The per-task pre-run brief the loop reads from before plan.</small>
</a>

<a href="../reference/runner-step-contracts.md">
<strong>Reference</strong>
<span>Runner step contracts</span>
<small>The typed shape every step request and step result carries.</small>
</a>

<a href="../reference/recovery.md">
<strong>Reference</strong>
<span>Recovery mode</span>
<small>The continuity view a resuming agent reads before acting.</small>
</a>

</div>
