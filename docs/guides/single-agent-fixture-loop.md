# Single-Agent Fixture Loop

Use fixture execution to smoke-test the loop boundary without live runner
credentials or external side effects.

## Workflow

1. Create or load a task, case file, policy envelope, and runner metadata.
2. Use `FixtureStepRunner` with deterministic statuses.
3. Pass explicit grants for side-effect fixture steps.
4. Execute `SingleAgentLoopExecutor`.
5. Inspect the resulting task run, receipts, run outputs, and proposals.

Minimal Python shape:

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

## Expected State

A successful fixture run should leave:

- one `craik.task_run`,
- one or more `craik.runner_step_result` observations,
- persisted `craik.run_output` records,
- pass or denial receipts for side-effect steps,
- optional reviewable memory proposals,
- and a handoff once the handoff workflow runs.

## Failure Smoke Tests

Use fixture statuses to exercise blocked, failed, partial, and max-iteration
paths. These runs should stop with durable state and should not rely on a live
chat transcript to explain what happened.
