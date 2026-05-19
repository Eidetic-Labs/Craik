# Claude runner adapter (preview)

<p className="craik-meta"><span>3 min read</span><span>Reference · preview</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The Claude preview adapter — local setup, fixture behavior, smoke
testing, and current limitations. The adapter implements Craik's
shared `RunnerAdapter` protocol for Claude-compatible workflows.

</div>

<div className="craik-keypoint">

**Prompt handoff and fixture output, not direct execution.**

In v0.1.0 the adapter focuses on prompt handoff and deterministic
fixture output rather than direct external execution.

</div>

## Local setup

```sh
craik prompt compile <task-id> --runner claude
```

Python callers:

```python
from craik.runtime.claude_adapter import ClaudeRunnerAdapter, request_from_compiled_prompt

adapter = ClaudeRunnerAdapter()
request = request_from_compiled_prompt(compiled_prompt, adapter=adapter)
result = adapter.run(request)
```

`ClaudeRunnerAdapter.metadata` keeps runner identity, adapter version,
fixture status, live availability, and optional executable details
inside `craik.runner_metadata.metadata`.

## Fixture behavior

Fixture mode is the default preview path. It produces a
`craik.runner_adapter_result` with:

<div className="craik-grid">

<div><h4><code>status</code></h4><p><code>completed</code> · <code>blocked</code> · <code>failed</code> · <code>partial</code>.</p></div>
<div><h4><code>outputs.prompt_handoff</code></h4><p>Compiled prompt for Claude-compatible use.</p></div>
<div><h4><code>outputs.handoff_input</code></h4><p>Normalized fields for a later handoff.</p></div>
<div><h4><code>outputs.receipt_inputs</code></h4><p>Normalized receipt drafts.</p></div>
<div><h4><code>outputs.runner_metadata</code></h4><p>Adapter metadata used for the run.</p></div>
<div><h4><code>diagnostics</code></h4><p>Live-execution limits and caller-supplied diagnostics.</p></div>

</div>

Tests can force a deterministic outcome:

```python
request = request_from_compiled_prompt(
    compiled_prompt,
    context={"fixture_status": "failed", "failure_reason": "missing transcript"},
)
```

## Smoke test

Use [Runner preview workflows](../guides/runner-preview-workflows.md)
to run completed, blocked, and failed fixture paths. Check
`outputs.runner_metadata`, `outputs.receipt_inputs`, and
`outputs.handoff_input` before promoting any adapter output into
receipts or handoffs.

## Limitations

<div className="craik-keypoint">

**No external Claude invocation.**

The preview adapter does not invoke an external Claude process or
verify Claude tool authority. Side effects must be treated as proposed
work until Craik can review and receipt them.

</div>

Live prompt handoff will need transcript capture, artifact capture,
receipt finalization, and explicit process/tool policy before it
should be used for side-effecting work.

## What's next

<div className="craik-next">

<a href="runner-adapter-contract/">
<strong>Reference</strong>
<span>Runner adapter contract</span>
<small>The shared contract.</small>
</a>

<a href="codex-runner-adapter/">
<strong>Reference</strong>
<span>Codex runner adapter</span>
<small>The Codex preview counterpart.</small>
</a>

<a href="../guides/runner-preview-workflows/">
<strong>Guide</strong>
<span>Runner preview workflows</span>
<small>End-to-end smoke testing.</small>
</a>

</div>
