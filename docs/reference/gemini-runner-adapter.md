# Gemini Runner Adapter Preview

The Gemini adapter preview implements Craik's shared `RunnerAdapter` protocol
for Gemini-compatible workflows. In v0.1.0 it is read/review-oriented and uses
prompt handoff plus deterministic fixture output rather than direct external
execution.

## Local Setup

Build a Gemini-targeted prompt first:

```sh
craik prompt compile <task-id> --runner gemini
```

Python callers can then create a request and run the adapter:

```python
from craik.runtime.gemini_adapter import GeminiRunnerAdapter, request_from_compiled_prompt

adapter = GeminiRunnerAdapter()
request = request_from_compiled_prompt(compiled_prompt, adapter=adapter)
result = adapter.run(request)
```

`GeminiRunnerAdapter.metadata` keeps runner identity, adapter version, fixture
status, live availability, and optional executable details inside
`craik.runner_metadata.metadata`.

## Fixture Behavior

Fixture mode is the default preview path. It produces a
`craik.runner_adapter_result` with:

- `status`: `completed`, `blocked`, `failed`, or `partial`,
- `outputs.prompt_handoff`: the compiled prompt for Gemini-compatible use,
- `outputs.handoff_input`: normalized fields suitable for a later handoff,
- `outputs.receipt_inputs`: normalized receipt drafts for granted capabilities,
- `outputs.runner_metadata`: the adapter metadata used for the run,
- `diagnostics`: live-execution limitations and caller-supplied diagnostics.

Tests can force a deterministic outcome through request context:

```python
request = request_from_compiled_prompt(
    compiled_prompt,
    context={"fixture_status": "blocked", "blocked_reason": "memory.write unsupported"},
)
```

## Smoke Test

Use the workflow in [Runner Preview Workflows](../guides/runner-preview-workflows.md)
to run completed, blocked, and failed fixture paths. Check
`outputs.runner_metadata`, `outputs.receipt_inputs`, and
`outputs.handoff_input` before promoting any adapter output into receipts or
handoffs.

## Limitations

The preview adapter does not invoke an external Gemini process or verify Gemini
tool authority. The built-in Gemini trust profile is intentionally low and
read/review-oriented; unsupported side effects should be blocked or routed back
through Craik review.

Live prompt handoff will need response capture, artifact capture, receipt
finalization, and explicit process/tool policy before it should be used for
side-effecting work.
