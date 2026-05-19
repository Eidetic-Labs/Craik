# Architecture

Craik is organized as a set of runtime layers. The layers should remain separable so Craik can support different model providers, tool environments, and memory backends without weakening the product thesis.

## Layers

### 1. Gateway Layer

The gateway receives human and machine requests, normalizes them, and creates runtime tasks.

Responsibilities:

- CLI, API, and UI entry points,
- auth context,
- project selection,
- task creation,
- initial policy envelope,
- and event streaming.

### 2. Project Model Layer

The project model layer builds the current working model for a task.

Inputs:

- repository state,
- issue and PR state,
- docs,
- ADRs and policies,
- recent agent handoffs,
- Stigmem facts,
- CI and release artifacts,
- and user-provided instructions.

Outputs:

- task case file,
- known constraints,
- relevant facts,
- stale-risk warnings,
- contradiction warnings,
- and required verification steps.

### 3. Orchestration Layer

The orchestration layer decomposes work and coordinates agents.

Responsibilities:

- role selection,
- model routing,
- task decomposition,
- parallel execution,
- specialist assignment,
- review loops,
- interruption handling,
- and stateful handoff creation.

The orchestrator should coordinate work, but it should not be the sole source of truth. Durable truth belongs in the memory substrate.

### 3a. Runner Adapter Layer

Runner adapters connect Craik contracts to concrete agent environments.

Initial first-class adapters:

- Codex,
- Claude,
- Gemini.

Responsibilities:

- translate case files into runner-specific task context,
- pass policy envelopes and capability grants to the runner,
- collect typed worker results,
- collect or create capability receipts,
- collect durable handoffs,
- translate runner-specific artifacts back into Craik contracts,
- and preserve enough metadata to make runs auditable.

The adapter layer should be thin. Craik core should own contracts, state, policy, receipts, handoffs, and memory integration. Runners should own model execution and environment-specific interaction.

### 4. Capability Layer

The capability layer exposes tools under explicit policy.

Capabilities include:

- file reads,
- file writes,
- shell commands,
- Git operations,
- GitHub operations,
- web search,
- package registries,
- CI inspection,
- memory reads,
- memory writes,
- and plugin execution.

Each capability should be scoped, auditable, and revocable.

### 5. Memory Layer

The memory layer stores and retrieves durable state.

Backends:

- ephemeral memory for tests and demos,
- local file or SQLite memory for single-user development,
- Stigmem memory for real team use.

Craik should depend on memory capabilities rather than hard-coding feature assumptions:

- durable facts,
- provenance,
- scopes,
- trust tiers,
- contradiction tracking,
- federation,
- and retention policy.

### 6. Work Graph Layer

The work graph connects runtime objects.

Node types:

- tasks,
- agents,
- handoffs,
- facts,
- decisions,
- issues,
- PRs,
- branches,
- files,
- docs,
- ADRs,
- commands,
- tests,
- CI runs,
- and generated artifacts.

Edges capture relationships such as "depends on", "created by", "verified by", "contradicts", "supersedes", "implements", and "blocks".

### 7. Experience Layer

Craik should expose the runtime through practical operator surfaces.

Initial surfaces:

- CLI,
- repository dashboard,
- task detail view,
- handoff viewer,
- contradiction inbox,
- work graph explorer,
- and capability receipt log.

## Runtime Flow

1. A user or system creates a task.
2. Craik creates a policy envelope.
3. Craik assembles a project case file.
4. The orchestrator selects agent roles and work decomposition.
5. Agents execute with scoped capabilities.
6. Tool use creates receipts.
7. Agents produce artifacts and findings.
8. Craik verifies required checks.
9. Memory updates are proposed or written according to policy.
10. A structured handoff is created.
11. The work graph is updated.

## Borrowed Patterns And Craik Extensions

| Source pattern | Craik adoption | Craik extension |
| --- | --- | --- |
| Gateway runtime | CLI/API gateway ergonomics inform entry points and session routing. | Gateway also creates policy envelopes and receipt obligations. |
| Workspace runtime | Project profile and local runtime state isolate work. | Case files and handoffs make workspace state portable across agents. |
| Skills runtime | Skills provide repeatable operating guidance. | Skills declare context contracts and capability requirements. |
| Tool descriptors | Tools are discovered as typed capabilities. | Capabilities require grants and produce receipts. |
| Orchestrator | Orchestrator decomposes complex tasks. | Orchestrator uses Stigmem-backed project memory and cannot flatten unresolved contradictions. |
| Specialists | Workers receive scoped context and return typed results. | Worker results become graph-linked artifacts and durable handoffs. |
| Task board | Task state survives the active run. | Task state becomes part of a work graph connected to facts, PRs, receipts, and decisions. |
| Codex, Claude, Gemini runners | Direct adapters execute work in real agent environments. | Adapters normalize outputs into Craik contracts and memory proposals. |

## Core Runtime Contracts

Craik should define stable schemas for:

- task requests,
- project case files,
- agent role manifests,
- capability grants,
- capability receipts,
- handoffs,
- facts proposed by agents,
- contradiction reports,
- verification results,
- and work graph events.

These contracts are more important than any single adapter language. Craik core starts as a Python 3.12/3.13 CLI runtime, while the contracts remain the basis for interoperability with Codex, Claude, Gemini, local agent runtimes, GitHub, CI, TypeScript gateways, UI surfaces, and Stigmem.
