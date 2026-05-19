# Single-agent fixture loop

<p className="craik-meta"><span>3 min read</span><span>For contributors</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Smoke-test the loop boundary with fixture execution — no live runner
credentials, no external side effects. Useful for development,
regression tests, and verifying durable-state contracts.

</div>

<div className="craik-keypoint">

**Same loop, deterministic runner.**

The fixture executor exercises the real loop boundary. Only the
runner-step results are deterministic; everything else (receipts, run
outputs, handoffs) follows the production contract.

</div>

## Workflow

<ol className="craik-steps">
<li>Create or load a task, case file, policy envelope, and runner metadata.</li>
<li>Use <code>FixtureStepRunner</code> with deterministic statuses.</li>
<li>Pass explicit grants for side-effect fixture steps.</li>
<li>Execute <code>SingleAgentLoopExecutor</code>.</li>
<li>Inspect the resulting task run, receipts, run outputs, and proposals.</li>
</ol>

## Minimal shape

```python
from craik.runtime.loop import FixtureStepRunner, SingleAgentLoopExecutor
from craik.runtime.memory import LocalMemoryStore

executor = SingleAgentLoopExecutor(
    store=store,
    memory=LocalMemoryStore(store),
    runner=FixtureStepRunner(),
)

result = executor.execute(
    task_id=task.id,
    case_file_id=case_file.id,
    policy=policy,
    runner_metadata=runner_metadata,
    intent_lock=intent_lock,
    grants=[shell_grant],
)
```

## Expected state

A successful fixture run leaves:

<div className="craik-grid">

<div><h4>One <code>craik.task_run</code></h4></div>
<div><h4>One or more <code>craik.runner_step_result</code> observations</h4></div>
<div><h4>Persisted <code>craik.run_output</code> records</h4></div>
<div><h4>Pass or denial receipts</h4><p>For side-effect steps.</p></div>
<div><h4>Optional reviewable memory proposals</h4></div>
<div><h4>A handoff</h4><p>Once the handoff workflow runs.</p></div>

</div>

## Failure smoke tests

<div className="craik-keypoint">

**Stop with durable state.**

Use fixture statuses to exercise blocked, failed, partial, and
max-iteration paths. These runs must stop with durable state and must
not rely on a live chat transcript to explain what happened.

</div>

## What's next

<div className="craik-next">

<a href="../../concepts/single-agent-loop/">
<strong>Concept</strong>
<span>Single-agent loop</span>
<small>The phase model and stop conditions the fixture exercises.</small>
</a>

<a href="../runner-preview-workflows/">
<strong>Guide</strong>
<span>Runner preview workflows</span>
<small>Move from fixtures to a real runner preview.</small>
</a>

<a href="../using-case-files/">
<strong>Guide</strong>
<span>Using case files</span>
<small>Assemble the case file the fixture run consumes.</small>
</a>

</div>
