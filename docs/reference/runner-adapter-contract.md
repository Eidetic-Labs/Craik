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
