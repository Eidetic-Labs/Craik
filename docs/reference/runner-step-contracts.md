# Runner Step Contracts

Runner steps are the contract boundary for the v0.3.0 single-agent execution
loop. They describe one bounded `plan`, `act`, `observe`, `evaluate`,
`continue`, or `stop` phase without invoking a runner by themselves.

## Step Requests

`craik.runner_step_request` contains:

- `run_id` and `task_id`,
- the loop `phase`,
- stable `runner` metadata,
- `policy_envelope_id` and optional `intent_lock_id`,
- capability grants and expected output schemas,
- an `input_prompt`,
- bounded `context`,
- and `redaction_required`.

The policy envelope and intent lock remain explicit so a runner step cannot
float away from the authority and scope that produced it.

## Step Results

`craik.runner_step_result` contains:

- the originating `request_id`,
- the same `run_id`, `task_id`, `phase`, and `runner` metadata,
- status: `completed`, `blocked`, `failed`, or `partial`,
- a human-readable summary,
- structured `observed_output`,
- diagnostics,
- receipt ids,
- memory proposal ids,
- artifacts,
- and a `redacted` flag.

Provider-specific details belong under structured output fields and must remain
redacted before persistence or handoff. Step contracts do not grant authority,
perform side effects, or decide continuation by themselves; the loop executor
will consume them with policy checks and task-run state.
