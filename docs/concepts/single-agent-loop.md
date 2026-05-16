# Single-Agent Execution Loop

Craik's v0.3.0 loop lets one runner work through a governed task without
depending on an untracked chat transcript. The runner still performs reasoning,
but Craik owns the durable boundary: run state, policy checks, receipts, step
outputs, memory proposals, and recovery state.

## Lifecycle

A run starts as `craik.task_run` with status `pending` and phase `plan`. The
executor moves through bounded steps:

| Phase | Purpose |
| --- | --- |
| `plan` | Decide the next bounded action. |
| `act` | Perform an approved side-effect or propose one. |
| `observe` | Capture output, diagnostics, receipts, and artifacts. |
| `evaluate` | Decide whether to stop, continue, block, or fail. |
| `continue` | Advance to another bounded iteration when needed. |
| `stop` | Finalize terminal state, handoff, receipts, and recovery context. |

Terminal statuses are `completed`, `blocked`, `failed`, and `interrupted`.
Interrupted runs preserve enough local state for inspection and later recovery.

## Safety Boundaries

Before each step, Craik checks the active intent lock. If a step triggers a
configured stop condition, the run stops before the runner receives another
request.

Side effects are policy-gated. A step such as shell execution must have a
matching capability grant before it runs. Denied side effects produce denial
receipts and block the run. Approved side effects produce pass receipts linked
to the run step.

`max_iterations` bounds the loop. Reaching that bound interrupts the run instead
of continuing indefinitely.

## Outputs And Memory

Runner output is captured as `craik.runner_step_result`, then persisted as a
redacted `craik.run_output`. Run outputs can create reviewable
`craik.memory_proposal` records, but they do not write durable facts directly.

Run-created proposals link to:

- the task id,
- the run id,
- the step result id,
- optional handoff id,
- and evidence pointing back to the captured run output.

Blocked and failed steps are still inspectable, but they do not create memory
proposals.

## Fixture Versus Live Runners

Fixture execution uses `FixtureStepRunner` and deterministic step statuses. It
is intended for local tests, docs, and executor contract checks.

Live runner execution uses adapter-specific boundaries. The same contracts
apply, but provider-specific details must stay under structured, redacted
metadata and may require stricter grants.

## Recovery

Recovery starts by inspecting the persisted run, receipts, outputs, memory
proposals, and handoff. Recovery should not replay side effects blindly. A
recovered run must re-check policy, intent-lock stop conditions, and iteration
limits before issuing another step request.
