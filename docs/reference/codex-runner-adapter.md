# Codex Runner Adapter Preview

The Codex adapter preview implements Craik's shared `RunnerAdapter` protocol for
Codex-compatible workflows. In v0.2.0 it is intentionally conservative: it can
turn a compiled prompt into a normalized runner request and return deterministic
fixture results when live execution is unavailable.

## Local Setup

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

`CodexRunnerAdapter.metadata` preserves runner identity, adapter version, mode,
fixture status, and live availability inside `craik.runner_metadata.metadata`.
Those fields are adapter details and do not expand the core contract surface.

## Fixture Behavior

Fixture mode is the default preview path. It produces a
`craik.runner_adapter_result` with:

- `status`: `completed`, `blocked`, `failed`, or `partial`,
- `outputs.prompt_handoff`: the compiled prompt for Codex-compatible execution,
- `outputs.handoff_input`: normalized fields suitable for a later handoff,
- `outputs.receipt_inputs`: normalized receipt drafts for granted capabilities,
- `outputs.runner_metadata`: the adapter metadata used for the run,
- `diagnostics`: live-execution limitations and caller-supplied diagnostics.

Tests can force a deterministic outcome through request context:

```python
request = request_from_compiled_prompt(
    compiled_prompt,
    context={"fixture_status": "blocked", "blocked_reason": "approval missing"},
)
```

## Limitations

The preview adapter does not invoke an external Codex process. It returns prompt
handoff and fixture outputs so Craik can validate policy, metadata, receipts,
and handoff wiring before live execution is enabled.

Live execution will need an explicit invocation policy, process isolation,
receipt finalization, and artifact capture before it should be used for
side-effecting work.
