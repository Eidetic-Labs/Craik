# Claude Runner Adapter Preview

The Claude adapter preview implements Craik's shared `RunnerAdapter` protocol
for Claude-compatible workflows. In v0.1.0 it focuses on prompt handoff and
deterministic fixture output rather than direct external execution.

## Local Setup

Build a Claude-targeted prompt first:

```sh
craik prompt compile <task-id> --runner claude
```

Python callers can then create a request and run the adapter:

```python
from craik.runtime.claude_adapter import ClaudeRunnerAdapter, request_from_compiled_prompt

adapter = ClaudeRunnerAdapter()
request = request_from_compiled_prompt(compiled_prompt, adapter=adapter)
result = adapter.run(request)
```

`ClaudeRunnerAdapter.metadata` keeps runner identity, adapter version, fixture
status, live availability, and optional executable details inside
`craik.runner_metadata.metadata`.

## Fixture Behavior

Fixture mode is the default preview path. It produces a
`craik.runner_adapter_result` with:

- `status`: `completed`, `blocked`, `failed`, or `partial`,
- `outputs.prompt_handoff`: the compiled prompt for Claude-compatible use,
- `outputs.handoff_input`: normalized fields suitable for a later handoff,
- `outputs.receipt_inputs`: normalized receipt drafts for granted capabilities,
- `outputs.runner_metadata`: the adapter metadata used for the run,
- `diagnostics`: live-execution limitations and caller-supplied diagnostics.

Tests can force a deterministic outcome through request context:

```python
request = request_from_compiled_prompt(
    compiled_prompt,
    context={"fixture_status": "failed", "failure_reason": "missing transcript"},
)
```

## Smoke Test

Use the workflow in [Runner Preview Workflows](../guides/runner-preview-workflows.md)
to run completed, blocked, and failed fixture paths. Check
`outputs.runner_metadata`, `outputs.receipt_inputs`, and
`outputs.handoff_input` before promoting any adapter output into receipts or
handoffs.

## Limitations

The preview adapter does not invoke an external Claude process or verify Claude
tool authority. Side effects should be treated as proposed work until Craik can
review and receipt them.

Live prompt handoff will need transcript capture, artifact capture, receipt
finalization, and explicit process/tool policy before it should be used for
side-effecting work.
