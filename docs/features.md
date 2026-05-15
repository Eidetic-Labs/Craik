# Feature Specification

This document turns Craik's product ideas into implementable features.

## Feature 1: Project Registry

Purpose: store known projects and their runtime configuration.

MVP behavior:

- `craik project add <path>` creates a project profile.
- Project profile records repo path, default branch, docs paths, immutable paths, and memory backend.
- Project profile can be printed as JSON.

Acceptance criteria:

- project can be added from a local Git repo,
- invalid paths fail with clear errors,
- immutable doc paths can be configured,
- and project profile schema validates.

## Feature 2: Case File Assembler

Purpose: build task-specific context before execution.

Inputs:

- task request,
- project profile,
- repository state,
- docs snippets,
- ADR/policy snippets,
- GitHub state when configured,
- Stigmem facts when configured,
- recent handoffs.

Outputs:

- case file JSON,
- human-readable Markdown case file,
- stale-risk list,
- contradiction list,
- verification plan.

Acceptance criteria:

- case file generation is deterministic for test fixtures,
- immutable ADR paths are clearly labeled,
- memory facts include source and confidence,
- stale-risk warnings are separated from verified facts,
- and output can be consumed by an agent prompt.

## Feature 3: Policy Envelope

Purpose: define execution authority and obligations.

MVP behavior:

- read-only tasks default to repo read, memory read, and receipt write.
- implementation tasks require explicit write grants.
- immutable paths cannot be written unless policy explicitly allows it.
- memory writes default to proposals unless configured for direct write.
- strict mode is the default policy profile.
- fail-open behavior is only available through named policy profiles.
- fail-open profile use appears in case files, receipts, and handoffs.

Acceptance criteria:

- denied file writes are blocked,
- denied memory writes become proposals,
- policy envelope is included in the case file,
- policy failures create receipts,
- trusted-local fail-open behavior requires explicit opt-in,
- and automation mode fails closed instead of widening permissions.

## Feature 4: Capability Receipts

Purpose: record important actions in a concise, queryable form.

Receipt-producing actions:

- file writes,
- shell commands,
- GitHub writes,
- memory writes,
- approvals,
- policy denials,
- contradiction opens/resolutions,
- handoff creation.

Acceptance criteria:

- receipts are persisted locally,
- receipts can be listed by task,
- receipt IDs appear in handoffs,
- receipts include actor, capability, target, reason, result, and timestamp,
- receipts include policy profile and fail-open status,
- and receipt payloads are redacted before persistence.

## Feature 5: Handoff Writer

Purpose: make agent work reusable by future agents.

MVP behavior:

- generate structured JSON handoff,
- generate Markdown handoff,
- link receipts,
- include memory proposals,
- include unresolved questions and next steps.

Acceptance criteria:

- every completed task has a handoff,
- handoff validates against schema,
- handoff includes verification status,
- and handoff can be loaded into a future case file.

## Feature 6: Memory Store Interface

Purpose: separate runtime from memory backend.

Backends:

- `EphemeralMemoryStore`,
- `LocalMemoryStore`,
- `StigmemMemoryStore`.

Required methods:

- `search_facts(query, scope)`,
- `list_facts(entity, relation)`,
- `propose_fact(proposal)`,
- `write_fact(fact)`,
- `invalidate_fact(fact_id, reason)`,
- `diff(run_id)`.

Acceptance criteria:

- all backends implement the same interface,
- tests run against ephemeral backend,
- local backend persists between CLI calls,
- and Stigmem backend can read/write facts with provenance.

## Feature 7: GitHub Adapter

Purpose: connect Craik tasks to live collaboration state.

MVP reads:

- repository metadata,
- open issues,
- open PRs,
- branch status,
- changed files,
- comments,
- CI/check status.

MVP writes:

- create issue,
- create PR,
- create comment.

Acceptance criteria:

- GitHub writes require capability grants,
- reads fail gracefully when unauthenticated,
- PR/issue references are included in case files,
- and created links appear in handoffs.

## Feature 8: Work Graph

Purpose: model agent work as connected state.

MVP nodes:

- task,
- handoff,
- fact,
- file,
- issue,
- PR,
- receipt,
- verification.

MVP edges:

- `created_by`,
- `depends_on`,
- `verified_by`,
- `updates`,
- `blocks`,
- `contradicts`.

Acceptance criteria:

- every task creates a task node,
- every handoff links to task and receipts,
- memory proposals link to evidence,
- and graph can be exported as JSON.

## Feature 9: Contradiction Inbox

Purpose: make disagreement operational.

MVP behavior:

- detect contradictions reported by agents,
- store contradiction reports,
- list open contradictions,
- resolve contradiction with rationale,
- create memory proposals from resolution.

Acceptance criteria:

- contradictions are not silently overwritten,
- resolution records evidence,
- affected artifacts can be listed,
- and resolved contradictions appear in memory diff.

## Feature 10: Memory Diff

Purpose: explain how memory changed during a run.

MVP behavior:

- list proposed facts,
- list written facts,
- list invalidated facts,
- list contradictions opened/resolved,
- list handoff facts created.

Acceptance criteria:

- memory diff can be printed for any task,
- diff is linked from handoff,
- and diff can be stored as a receipt artifact.

## Feature 11: Orchestrator And Specialists

Purpose: support multi-agent workflows after the single-agent loop works.

MVP roles:

- orchestrator,
- researcher,
- docs reviewer,
- implementer,
- verifier,
- adjudicator.

Behavior:

- orchestrator decomposes task into child tasks,
- specialists receive case-file excerpts,
- specialists return typed worker results,
- orchestrator merges results into handoff,
- contradictions are escalated instead of flattened.

Acceptance criteria:

- independent read-only tasks can run in parallel,
- worker outputs validate against schema,
- child handoffs link to parent task,
- and orchestrator cannot discard unresolved contradictions.

## Feature 11a: First-Class Runner Adapters

Purpose: let Craik work directly with real agent runners instead of requiring a separate agent framework as an execution layer.

Initial adapters:

- Codex,
- Claude,
- Gemini.

Adapter responsibilities:

- receive task request, case file, policy envelope, and grants,
- start or guide a runner session,
- preserve runner identity and version metadata,
- capture typed worker results,
- capture receipts or receipt inputs,
- capture handoff output,
- return proposed memory updates,
- and report blocks, failures, or missing capabilities.

Acceptance criteria:

- each adapter implements the same runner interface,
- adapter outputs validate against Craik contracts,
- runner-specific details do not leak into core contracts,
- unsupported capabilities fail clearly,
- and a task can be replayed or inspected from Craik artifacts without relying on raw chat history.

OpenClaw-style integration should be tracked as a later bridge, not a dependency for this feature.

## Feature 12: Skills And Plugins

Purpose: make repeated workflows reusable while keeping authority governed.

MVP behavior:

- skills are instruction packages scoped to project or runtime,
- plugins expose typed capabilities,
- plugin capabilities require grants,
- plugin actions produce receipts,
- probationary plugins have restricted permissions.
- plugins cannot bypass runner or task policy envelopes.

Acceptance criteria:

- project-scoped skills override global skills,
- skills can declare required context contracts,
- plugin descriptors validate,
- and probationary plugin use is visible in receipts.

## Feature 13: Context Contracts

Purpose: define what context a task type must receive.

Examples:

- docs review requires docs paths, implementation references, ADR policy, recent facts, stale-risk list.
- implementation requires branch state, test commands, capability grants, relevant issues, coding conventions.
- release work requires version policy, changelog policy, package registry state, CI requirements.

Acceptance criteria:

- missing required context blocks execution or creates a warning,
- case file marks satisfied and missing context,
- and roles can declare required context contracts.

## Feature 14: Agent Reputation

Purpose: measure reliability without turning it into popularity.

Signals:

- facts later contradicted,
- tests passed/failed after edits,
- policy violations,
- handoff completeness,
- review findings accepted,
- tasks completed without rework.

Acceptance criteria:

- reputation is scoped by role/domain,
- metrics are explainable,
- and reputation affects routing only when policy enables it.

This feature should not be part of the MVP implementation, but contracts should leave room for it.
