# Run State

Craik persists each governed single-agent execution as `craik.task_run`.

A task run links the task request, case file, policy envelope, runner identity,
optional intent lock, receipts, and final handoff. It gives later loop
orchestration an inspectable record without depending on an untracked chat
transcript.

## Lifecycle

Run status values:

| Status | Meaning |
| --- | --- |
| `pending` | The run has been created but has not started side effects. |
| `running` | The run is actively moving through loop phases. |
| `completed` | The run finished the task and wrote final state. |
| `blocked` | The run stopped because required context or approval is missing. |
| `failed` | The run stopped because execution failed. |
| `interrupted` | The run stopped before completion and can be inspected for recovery. |

Run phase values:

| Phase | Meaning |
| --- | --- |
| `plan` | Build or refresh the execution plan. |
| `act` | Perform one governed action. |
| `observe` | Capture action output and receipts. |
| `evaluate` | Decide whether the goal is satisfied or blocked. |
| `continue` | Advance to another bounded iteration. |
| `stop` | Finalize receipts, handoff, and terminal status. |

`started_at`, `phase_started_at`, `updated_at`, and `ended_at` capture
deterministic lifecycle timing. The `iteration` and `max_iterations` fields
bound the loop before the executor exists.

## Persistence

`LocalStore` stores task runs as validated JSON under the `task_runs` kind and
exposes typed helpers:

- `put_task_run`
- `get_task_run`
- `list_task_runs`

`TaskRunManager` creates deterministic run ids and enforces basic transition
rules: terminal runs cannot transition again, iteration counts cannot exceed
`max_iterations`, phase changes refresh `phase_started_at`, and terminal
statuses set `ended_at`.

## Execution Loop

`SingleAgentLoopExecutor` drives fixture-compatible single-agent runs through
bounded steps. Before each step it checks intent-lock stop conditions, verifies
policy for configured side effects, records denial or pass receipts, sends a
`craik.runner_step_request` to the runner boundary, captures the
`craik.runner_step_result` as `craik.run_output`, and advances task-run state.

The default deterministic loop uses `plan`, `act`, `observe`, and `evaluate`.
The `act` phase is treated as a side-effect step and requires a matching policy
grant. Reaching `max_iterations`, a runner failure, a blocked runner result, or
an intent stop condition stops the run before additional side effects.

See [Single-Agent Execution Loop](../concepts/single-agent-loop.md) for the
conceptual lifecycle and [Single-Agent Fixture Loop](../guides/single-agent-fixture-loop.md)
for the deterministic smoke-test workflow.
