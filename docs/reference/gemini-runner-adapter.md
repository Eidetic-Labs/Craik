# Gemini runner adapter (preview)

<p className="craik-meta"><span>3 min read</span><span>Reference · preview</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The Gemini preview adapter — local setup, fixture behavior, smoke
testing, and limitations. In v0.1.0 the adapter is read/review-oriented
and uses prompt handoff plus deterministic fixture output rather than
direct external execution.

</div>

<div className="craik-keypoint">

**Read/review-oriented by default.**

The built-in Gemini trust profile is intentionally low. Unsupported
side effects are blocked or routed back through Craik review.

</div>

## Local setup

```sh
craik prompt compile <task-id> --runner gemini
```

Python callers:

```python
from craik.runtime.gemini_adapter import GeminiRunnerAdapter, request_from_compiled_prompt

adapter = GeminiRunnerAdapter()
request = request_from_compiled_prompt(compiled_prompt, adapter=adapter)
result = adapter.run(request)
```

`GeminiRunnerAdapter.metadata` keeps runner identity, adapter version,
fixture status, live availability, and optional executable details
inside `craik.runner_metadata.metadata`.

## Fixture behavior

Fixture mode is the default preview path. It produces a
`craik.runner_adapter_result` with:

<div className="craik-grid">

<div><h4><code>status</code></h4><p><code>completed</code> · <code>blocked</code> · <code>failed</code> · <code>partial</code>.</p></div>
<div><h4><code>outputs.prompt_handoff</code></h4><p>Compiled prompt for Gemini-compatible use.</p></div>
<div><h4><code>outputs.handoff_input</code></h4><p>Normalized fields for a later handoff.</p></div>
<div><h4><code>outputs.receipt_inputs</code></h4><p>Normalized receipt drafts.</p></div>
<div><h4><code>outputs.runner_metadata</code></h4><p>Adapter metadata used for the run.</p></div>
<div><h4><code>diagnostics</code></h4><p>Live-execution limits and caller-supplied diagnostics.</p></div>

</div>

Force a deterministic outcome:

```python
request = request_from_compiled_prompt(
    compiled_prompt,
    context={"fixture_status": "blocked", "blocked_reason": "memory.write unsupported"},
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

**No external Gemini invocation.**

The preview adapter does not invoke an external Gemini process or
verify Gemini tool authority.

</div>

Live prompt handoff will need response capture, artifact capture,
receipt finalization, and explicit process/tool policy before it
should be used for side-effecting work.

## What's next

<div className="craik-next">

<a href="../runner-adapter-contract/">
<strong>Reference</strong>
<span>Runner adapter contract</span>
<small>The shared contract.</small>
</a>

<a href="../codex-runner-adapter/">
<strong>Reference</strong>
<span>Codex runner adapter</span>
<small>The Codex preview counterpart.</small>
</a>

<a href="../../guides/runner-preview-workflows/">
<strong>Guide</strong>
<span>Runner preview workflows</span>
<small>End-to-end smoke testing.</small>
</a>

</div>
