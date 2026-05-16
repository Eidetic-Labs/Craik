# Prompt Compiler

`craik prompt compile` turns existing Craik runtime state into a deterministic
runner-ready prompt. It does not invoke a runner. It prepares the prompt boundary
for adapter previews.

## Command

```sh
craik prompt compile <task-id> --runner <runner-id>
```

Options:

- `--runner <runner-id>`: runner id from `craik runners matrix`.
- `--expected-output-schema <schema>`: output schema to request. May be repeated.

The command persists and prints a `craik.compiled_prompt` contract.

## Inputs

The compiler reads:

- the `craik.task_request`,
- the latest `craik.case_file` for the task,
- the referenced `craik.policy_envelope`, or a deterministic strict fallback,
- task-scoped `craik.capability_grant` records,
- the selected `craik.runner_capability_matrix`,
- context-budget omissions and discovery exclusions,
- assumptions, stale risks, contradictions, docs, and immutable docs from the
  case file,
- and expected output schemas.

## Output

`craik.compiled_prompt` includes:

- task, case file, policy, and runner ids,
- runner mode,
- capability grant ids,
- expected output schemas,
- context omissions,
- stop conditions,
- named prompt sections,
- and the rendered prompt text.

The rendered prompt has stable section order so fixture tests can compare output
across runs.

## Policy Boundary

The compiler makes policy visible; it does not grant authority. Runners still
need explicit grants for side effects, and unsupported runner capabilities should
not be requested. Omitted context, assumptions, and stale risks are surfaced so a
runner can stop or ask for more context instead of treating missing context as
evidence.

See [Runner Preview Workflows](../guides/runner-preview-workflows.md) for the
full compile, fixture, receipt, and handoff flow.
