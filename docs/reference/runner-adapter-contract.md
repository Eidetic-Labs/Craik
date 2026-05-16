# Runner Adapter Contract

Runner adapters are the boundary between Craik core and concrete agent
environments. The contract is intentionally runner-agnostic: adapters receive
Craik state and return normalized Craik state without leaking provider-specific
details into core contracts.

## Contracts

`craik.runner_metadata` records stable adapter identity:

- runner id and display name,
- adapter id and adapter version,
- execution mode: `fixture`, `prompt-handoff`, or `live`,
- capability names,
- and structured adapter metadata.

`craik.runner_adapter_request` is the input from Craik core to an adapter:

- task id,
- runner metadata,
- task request id,
- case file id,
- policy envelope id,
- capability grant ids,
- expected output schemas,
- and bounded context prepared by Craik.

`craik.runner_adapter_result` is the normalized adapter output:

- status: `completed`, `blocked`, `failed`, or `partial`,
- summary,
- structured outputs,
- receipt ids,
- optional handoff id,
- memory proposal ids,
- artifacts,
- diagnostics,
- and runner metadata.

`craik.runner_capability_matrix` records the stable capability and trust profile
Craik uses before selecting or prompting a runner:

- runner metadata,
- trust level and boundary,
- default grant posture,
- whether receipts and redaction are required,
- normalized capability entries,
- and policy notes.

Capability support is one of:

- `unsupported`: the runner should not be asked to perform the action,
- `prompt-handoff`: the runner can reason about or propose the action, but Craik
  must route side effects through review,
- `supported`: the runner can perform the action when policy grants allow it.

Side-effect capabilities default to `grant_required: true`. Read-only context and
structured-result capabilities may be marked grant-free when the runner profile
can consume them without widening authority.

## Adapter Interface

Python adapters implement the `RunnerAdapter` protocol:

```python
from craik.runtime.runners import RunnerAdapter


def run_task(adapter: RunnerAdapter, request):
    return adapter.run(request)
```

Adapters must validate the request they receive, preserve runner metadata, and
return a `craik.runner_adapter_result` payload. Fixture adapters can use
`FixtureRunnerAdapter` for deterministic contract tests without live runner
credentials.

## Capability Matrix

Built-in preview matrices are exposed through:

```sh
craik runners matrix
craik runners matrix --runner codex
```

The v0.2.0 preview profiles are conservative:

- `codex`: live local runner, medium trust, side effects require explicit grants
  and receipts.
- `claude`: prompt-handoff runner, medium trust, side effects return through
  Craik review and receipt workflows.
- `gemini`: prompt-handoff runner, low trust until adapter tests justify broader
  authority.
- `fixture`: deterministic test runner with no external side effects.

Future prompt compilation and policy decisions should consume
`craik.runner_capability_matrix` rather than inferring authority from a runner
name or free-form metadata.

## Boundaries

Craik core owns:

- task requests,
- case files,
- policy envelopes,
- capability grants,
- receipts,
- handoffs,
- memory proposals,
- and contract validation.

Adapters own:

- runner invocation or prompt handoff,
- runner-specific session details,
- runner-specific diagnostics,
- and mapping runner output back into Craik contracts.

Runner-specific details should stay inside the `metadata`, `outputs`, or
`diagnostics` fields unless they become stable cross-runner contract fields.
