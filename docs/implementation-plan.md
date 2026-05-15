# Implementation Plan

This plan turns the Craik concept into a buildable sequence.

## Recommended Stack

The initial implementation should optimize for fast, testable CLI development.

Recommended default:

- Python 3.12+,
- Typer or Click for CLI,
- Pydantic for schema validation,
- SQLite for local persistent state,
- `httpx` for Stigmem and GitHub API calls,
- `pytest` for tests,
- `ruff` and `mypy` for quality gates.

Rationale:

- Stigmem already has Python surfaces.
- Pydantic makes versioned contracts straightforward.
- SQLite is enough for local task, receipt, handoff, and work graph state.
- CLI-first keeps the MVP focused.

## Repository Shape

Initial structure:

```text
craik/
  __init__.py
  cli.py
  contracts/
    task.py
    project.py
    policy.py
    case_file.py
    receipt.py
    handoff.py
    memory.py
    graph.py
  runtime/
    project_registry.py
    case_assembler.py
    executor.py
    handoff_writer.py
    receipt_store.py
    policy_engine.py
  memory/
    base.py
    ephemeral.py
    local.py
    stigmem.py
  adapters/
    repo.py
    github.py
  orchestration/
    roles.py
    orchestrator.py
    worker_result.py
  graph/
    store.py
    export.py
tests/
docs/
```

## Milestone 1: Contract Foundation

Build:

- package skeleton,
- CLI skeleton,
- Pydantic models for core contracts,
- schema version fields,
- JSON serialization/deserialization,
- validation tests.

Commands:

- `craik version`
- `craik schema list`
- `craik schema show <name>`

Acceptance criteria:

- all schemas validate sample fixtures,
- invalid fixtures produce clear errors,
- docs examples match real schemas,
- and CI runs lint/type/test checks.

## Milestone 2: Project Registry And Local State

Build:

- SQLite local store,
- project registry,
- local config directory,
- repo detection,
- immutable path config,
- local memory backend.

Commands:

- `craik init`
- `craik project add <path>`
- `craik project list`
- `craik project show <id>`

Acceptance criteria:

- project can be registered from Git repo,
- registry persists between commands,
- project profile validates,
- and immutable path policy is stored.

## Milestone 3: Case File Assembly

Build:

- repository adapter,
- branch/diff inspection,
- docs discovery,
- ADR/policy discovery,
- Stigmem/local fact loading,
- stale-risk section,
- verification-plan section,
- Markdown and JSON output.

Commands:

- `craik task create --project <id> --title "..."`
- `craik case build <task-id>`
- `craik case show <task-id>`

Acceptance criteria:

- case file includes repo status,
- docs and immutable paths are labeled,
- facts include source/confidence,
- output is deterministic for fixtures,
- and missing context is clearly reported.

## Milestone 4: Policy And Receipts

Build:

- policy envelope generation,
- capability grant model,
- receipt store,
- policy denial receipts,
- shell command receipt wrapper,
- file write receipt wrapper.

Commands:

- `craik policy show <task-id>`
- `craik receipts list <task-id>`
- `craik receipts show <receipt-id>`

Acceptance criteria:

- denied writes are blocked,
- allowed actions create receipts,
- shell command results are summarized,
- and receipts link back to task and policy envelope.

## Milestone 5: Handoff Loop

Build:

- structured handoff writer,
- Markdown handoff writer,
- handoff validation,
- handoff load into case file,
- memory proposal attachment.

Commands:

- `craik handoff create <task-id>`
- `craik handoff show <task-id>`
- `craik handoff list --project <id>`

Acceptance criteria:

- every completed task can produce a handoff,
- handoff includes receipts,
- handoff includes verification state,
- handoff is loaded into the next related case file,
- and handoff schema validates.

## Milestone 6: Stigmem Backend

Build:

- Stigmem config,
- API key setup,
- fact search/read/write,
- fact proposal mapping,
- handoff summary fact writes,
- memory diff for task runs.

Commands:

- `craik connect stigmem --url <url>`
- `craik memory search <query>`
- `craik memory propose <task-id>`
- `craik memory diff <task-id>`

Acceptance criteria:

- Craik can connect to a local Stigmem node,
- failed auth has a clear error,
- facts are included in case files,
- proposed facts can be reviewed before write,
- and written facts include provenance.

## Milestone 7: GitHub Adapter

Build:

- GitHub auth detection,
- repo mapping,
- issue/PR reads,
- changed-file reads,
- check status reads,
- guarded issue/PR/comment writes.

Commands:

- `craik github status <project-id>`
- `craik github issues <project-id>`
- `craik github prs <project-id>`

Acceptance criteria:

- case file includes relevant GitHub state,
- GitHub writes require grants,
- created links appear in handoff,
- and unauthenticated mode remains usable for local-only tasks.

## Milestone 8: Work Graph

Build:

- graph node/event models,
- graph store,
- export command,
- task/handoff/fact/receipt graph links,
- contradiction graph links.

Commands:

- `craik graph export <project-id>`
- `craik graph show-task <task-id>`

Acceptance criteria:

- each task creates graph nodes,
- handoffs and receipts are linked,
- fact proposals link to evidence,
- and graph export is deterministic.

## Milestone 9: Contradictions And Memory Diff

Build:

- contradiction report model,
- contradiction store,
- contradiction list/show/resolve commands,
- memory diff command,
- resolution-to-memory-proposal flow.

Commands:

- `craik contradictions list`
- `craik contradictions show <id>`
- `craik contradictions resolve <id>`
- `craik memory diff <task-id>`

Acceptance criteria:

- contradictions can be opened by an agent or user,
- contradictions are not overwritten by later facts,
- resolutions record rationale,
- and memory diff includes contradiction state.

## Milestone 10: Multi-Agent Orchestration

Build after the single-agent durable loop works.

Build:

- role manifests,
- orchestrator task decomposition,
- child task creation,
- worker result validation,
- specialist handoffs,
- parent handoff merge,
- parallel read-only execution.

Commands:

- `craik roles list`
- `craik task split <task-id>`
- `craik task run --multi-agent <task-id>`

Acceptance criteria:

- specialists receive scoped case files,
- worker results validate,
- child handoffs link to parent,
- read-only work can run in parallel,
- and unresolved contradictions block flattening into a final answer.

## Milestone 11: Skills And Probationary Plugins

Build:

- skill directory discovery,
- project-scoped skills,
- global skills,
- context contract declarations,
- plugin descriptor model,
- probationary plugin policy,
- plugin receipt requirements.

Acceptance criteria:

- skills alter case-file guidance without changing code,
- project skills override global skills,
- plugins expose typed capabilities,
- probationary plugins have limited grants,
- and plugin use appears in receipts.

## First End-To-End Scenario

Target scenario:

1. Register `Eidetic-Labs/stigmem`.
2. Connect to local Stigmem.
3. Create a docs reconciliation task.
4. Build a case file from repo docs, ADRs, facts, and GitHub state.
5. Run a governed agent with docs-write capability.
6. Capture receipts for file writes and validation commands.
7. Generate a handoff.
8. Propose or write facts about the new state.
9. Export work graph for the task.

This scenario should be automated as a fixture-driven integration test before broadening the platform.

## Deferred Decisions

These should be decided before coding starts, but they should not block the planning docs:

- license,
- package name,
- whether the public CLI command is `craik`,
- hosted service posture,
- default local state directory,
- exact relationship to existing Eidetic auth,
- and whether the first UI is built into Craik or kept separate.
