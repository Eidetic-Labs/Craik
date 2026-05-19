# Codex runner adapter (preview)

<p className="craik-meta"><span>3 min read</span><span>Reference · preview</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The Codex preview adapter — how to set it up, fixture behavior, smoke
testing, and current limitations. The adapter implements Craik's
shared `RunnerAdapter` protocol for Codex-compatible workflows and is
intentionally conservative in v0.1.0.

</div>

<div className="craik-keypoint">

**Preview, not live execution.**

The adapter turns a compiled prompt into a normalized runner request
and returns deterministic fixture results. Live external execution is
not part of v0.1.0.

</div>

## Local setup

Build the prompt first:

```sh
craik prompt compile <task-id> --runner codex
```

Python callers can then create a request and run the adapter:

```python
from craik.runtime.codex_adapter import CodexRunnerAdapter, request_from_compiled_prompt

adapter = CodexRunnerAdapter()
request = request_from_compiled_prompt(compiled_prompt, adapter=adapter)
result = adapter.run(request)
```

`CodexRunnerAdapter.metadata` preserves runner identity, adapter
version, mode, fixture status, and live availability inside
`craik.runner_metadata.metadata`. Those fields are adapter details
and do not expand the core contract surface.

## Fixture behavior

Fixture mode is the default preview path. It produces a
`craik.runner_adapter_result` with:

<div className="craik-grid">

<div><h4><code>status</code></h4><p><code>completed</code> · <code>blocked</code> · <code>failed</code> · <code>partial</code>.</p></div>
<div><h4><code>outputs.prompt_handoff</code></h4><p>The compiled prompt for Codex-compatible execution.</p></div>
<div><h4><code>outputs.handoff_input</code></h4><p>Normalized fields suitable for a later handoff.</p></div>
<div><h4><code>outputs.receipt_inputs</code></h4><p>Normalized receipt drafts for granted capabilities.</p></div>
<div><h4><code>outputs.runner_metadata</code></h4><p>The adapter metadata used for the run.</p></div>
<div><h4><code>diagnostics</code></h4><p>Live-execution limitations and caller-supplied diagnostics.</p></div>

</div>

Tests can force a deterministic outcome through request context:

```python
request = request_from_compiled_prompt(
    compiled_prompt,
    context={"fixture_status": "blocked", "blocked_reason": "approval missing"},
)
```

## Smoke test

Use the workflow in
[Runner preview workflows](../guides/runner-preview-workflows.md) to
run completed, blocked, and failed fixture paths. Check
`outputs.runner_metadata`, `outputs.receipt_inputs`, and
`outputs.handoff_input` before promoting any adapter output into
receipts or handoffs.

## Limitations

<div className="craik-keypoint">

**No external Codex invocation.**

The preview adapter returns prompt handoff and fixture outputs so
Craik can validate policy, metadata, receipts, and handoff wiring
before live execution is enabled.

</div>

Live execution will need explicit invocation policy, process
isolation, receipt finalization, and artifact capture before it should
be used for side-effecting work.

## What's next

<div className="craik-next">

<a href="runner-adapter-contract/">
<strong>Reference</strong>
<span>Runner adapter contract</span>
<small>The shared contract.</small>
</a>

<a href="claude-runner-adapter/">
<strong>Reference</strong>
<span>Claude runner adapter</span>
<small>The Claude preview counterpart.</small>
</a>

<a href="../guides/runner-preview-workflows/">
<strong>Guide</strong>
<span>Runner preview workflows</span>
<small>End-to-end smoke testing.</small>
</a>

</div>
