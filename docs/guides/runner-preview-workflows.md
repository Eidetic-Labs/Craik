# Runner Preview Workflows

Craik's v0.1.0 runner adapter and provider-adapter surface connects four pieces:

- context discovery and case files,
- policy-aware prompt compilation,
- runner adapter fixture or prompt-handoff execution,
- receipt and handoff metadata capture.

The preview is designed to validate runner boundaries before live side effects
are trusted. Fixture mode, prompt handoff, and governed provider execution are
the expected paths.

## Workflow

1. Register or select a project.
2. Create a task with explicit scope, constraints, and expected outputs.
3. Build the task case file.
4. Compile a runner-targeted prompt.
5. Build a runner adapter request from the compiled prompt.
6. Run the preview adapter in fixture or prompt-handoff mode.
7. Persist receipts and handoffs from the normalized result when appropriate.
8. Review runner metadata, policy boundaries, omitted context, and diagnostics
   before treating output as evidence.

## Context And Overrides

Case files decide what context reaches the prompt. Configure project docs,
immutable paths, discovery includes, and discovery excludes before building the
case file. See [Using Case Files](using-case-files.md), [Context
Budgeting](context-budgeting.md), and [Project Registry](project-registry.md).

Compiled prompts surface omitted or excluded context in
`context_omissions`. Runners should treat omissions as stop-or-ask conditions,
not as evidence that omitted material is irrelevant.

## Compile A Prompt

Use the runner capability matrix to choose the runner:

```sh
craik runners matrix
craik runners matrix --runner codex
```

Compile the prompt:

```sh
craik prompt compile <task-id> --runner codex
craik prompt compile <task-id> --runner claude
craik prompt compile <task-id> --runner gemini
```

The compiler persists a `craik.compiled_prompt` and includes:

- task and policy boundaries,
- capability grants,
- runner trust profile,
- unsupported or prompt-handoff capabilities,
- context omissions,
- expected output schemas,
- stop conditions.

## Run A Preview Adapter

Each preview adapter implements the same runtime shape:

```python
from craik.runtime.codex_adapter import CodexRunnerAdapter, request_from_compiled_prompt

adapter = CodexRunnerAdapter()
request = request_from_compiled_prompt(compiled_prompt, adapter=adapter)
result = adapter.run(request)
```

Use the matching module for each runner:

- `craik.runtime.codex_adapter`
- `craik.runtime.claude_adapter`
- `craik.runtime.gemini_adapter`

Fixture outcomes are controlled through request context:

```python
request = request_from_compiled_prompt(
    compiled_prompt,
    context={
        "fixture_status": "blocked",
        "blocked_reason": "missing approval for shell.execute",
    },
)
```

Supported fixture statuses are `completed`, `blocked`, `failed`, and `partial`.

## Result Shape

Adapters return `craik.runner_adapter_result` with:

- `outputs.prompt_handoff`: the compiled prompt and runner id,
- `outputs.receipt_inputs`: receipt draft inputs for granted capabilities,
- `outputs.handoff_input`: fields suitable for handoff creation,
- `outputs.runner_metadata`: stable runner, adapter, trust, and capability
  metadata,
- `diagnostics`: fixture and prompt-handoff limitations or runner diagnostics.

Receipts and handoffs preserve stable runner metadata so future agents can see
which adapter, version, execution mode, trust profile, and capability profile
were involved. Runner-specific fields remain nested and redacted.

## Policy Boundary

Preview adapters do not grant authority. The policy boundary remains:

- side effects require explicit capability grants,
- unsupported capabilities should be blocked,
- prompt-handoff side effects must return through Craik review,
- fixture results are deterministic test outputs, not proof of live execution,
- receipt metadata describes runner context but does not replace concrete
  side-effect receipts.

## Smoke Test Checklist

For a local preview smoke test:

- run `craik runners matrix --runner <id>` and confirm the trust profile,
- run `craik prompt compile <task-id> --runner <id>`,
- build a request with the matching adapter module,
- run one `completed`, one `blocked`, and one `failed` fixture path,
- confirm `outputs.runner_metadata`, `outputs.receipt_inputs`, and
  `outputs.handoff_input` are present,
- confirm secrets in runner-specific metadata are redacted,
- run the project validation command from
  [Development Checks](development.md).

## Reference

- [Runner Adapter Contract](../reference/runner-adapter-contract.md)
- [Prompt Compiler](../reference/prompt-compiler.md)
- [Runner Metadata](../reference/runner-metadata.md)
- [Codex Runner Adapter](../reference/codex-runner-adapter.md)
- [Claude Runner Adapter](../reference/claude-runner-adapter.md)
- [Gemini Runner Adapter](../reference/gemini-runner-adapter.md)
