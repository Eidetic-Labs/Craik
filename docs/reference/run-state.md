# Run state

<p className="craik-meta"><span>3 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `craik.task_run` lifecycle — status values, loop phases,
persistence helpers, and the executor that drives bounded fixture-
compatible runs.

</div>

<div className="craik-keypoint">

**Inspection without transcripts.**

A task run links the task request, case file, policy envelope, runner
identity, optional intent lock, receipts, and final handoff. It gives
later loop orchestration an inspectable record without depending on an
untracked chat transcript.

</div>

## Status values

| Status | Meaning |
| --- | --- |
| `pending` | The run has been created but has not started side effects. |
| `running` | The run is actively moving through loop phases. |
| `completed` | The run finished the task and wrote final state. |
| `blocked` | The run stopped because required context or approval is missing. |
| `failed` | The run stopped because execution failed. |
| `interrupted` | The run stopped before completion and can be inspected for recovery. |

## Phase values

| Phase | Meaning |
| --- | --- |
| `plan` | Build or refresh the execution plan. |
| `act` | Perform one governed action. |
| `observe` | Capture action output and receipts. |
| `evaluate` | Decide whether the goal is satisfied or blocked. |
| `continue` | Advance to another bounded iteration. |
| `stop` | Finalize receipts, handoff, and terminal status. |

`started_at`, `phase_started_at`, `updated_at`, and `ended_at`
capture deterministic lifecycle timing. The `iteration` and
`max_iterations` fields bound the loop before the executor exits.

## Persistence

`LocalStore` stores task runs as validated JSON under the `task_runs`
kind and exposes typed helpers:

<div className="craik-grid">

<div><h4><code>put_task_run</code></h4></div>
<div><h4><code>get_task_run</code></h4></div>
<div><h4><code>list_task_runs</code></h4></div>

</div>

<div className="craik-keypoint">

**Transition rules are enforced.**

<code>TaskRunManager</code> creates deterministic run ids and enforces
transition rules: terminal runs cannot transition again, iteration
counts cannot exceed <code>max_iterations</code>, phase changes
refresh <code>phase_started_at</code>, and terminal statuses set
<code>ended_at</code>.

</div>

## Execution loop

`SingleAgentLoopExecutor` drives fixture-compatible single-agent runs
through bounded steps.

<ol className="craik-steps">
<li>Check intent-lock stop conditions.</li>
<li>Verify policy for configured side effects.</li>
<li>Record denial or pass receipts.</li>
<li>Send a <code>craik.runner_step_request</code> to the runner boundary.</li>
<li>Capture the <code>craik.runner_step_result</code> as <code>craik.run_output</code>.</li>
<li>Advance task-run state.</li>
</ol>

<div className="craik-keypoint">

**Defaults are conservative.**

The default deterministic loop uses <code>plan</code> · <code>act</code>
· <code>observe</code> · <code>evaluate</code>. The <code>act</code>
phase is treated as a side-effect step and requires a matching policy
grant. Reaching <code>max_iterations</code>, a runner failure, a
blocked runner result, or an intent stop condition stops the run
before additional side effects.

</div>

## What's next

<div className="craik-next">

<a href="../../concepts/single-agent-loop/">
<strong>Concept</strong>
<span>Single-agent execution loop</span>
<small>The conceptual lifecycle.</small>
</a>

<a href="../../guides/single-agent-fixture-loop/">
<strong>Guide</strong>
<span>Single-agent fixture loop</span>
<small>The deterministic smoke-test workflow.</small>
</a>

<a href="../runner-step-contracts/">
<strong>Reference</strong>
<span>Runner step contracts</span>
<small>The per-step request and result shapes.</small>
</a>

</div>
