# Product Strategy

Craik should build on the strengths of OpenClaw and Hermes without becoming a clone of either.

The opportunity is to combine the approachable local-agent ergonomics of OpenClaw, the multi-agent decomposition patterns of Hermes, and Stigmem's durable memory/truth substrate into a new product category: a durable runtime for agent organizations.

## What To Borrow From OpenClaw

OpenClaw's strongest lessons are operational and ergonomic.

Reference sources:

- OpenClaw agent runtime documentation: https://docs.openclaw.ai/agent
- OpenClaw workspace documentation: https://docs.openclaw.ai/agent-workspace
- OpenClaw tools and skills documentation: https://docs.openclaw.ai/tools

Craik should adopt:

- **Self-hosted first:** users should be able to run the runtime locally or on their own infrastructure.
- **Gateway model:** one entry point should connect users, agents, tools, sessions, and channels.
- **Workspace identity:** each agent/project should have a clear workspace with scoped files, runtime config, and persistent session artifacts.
- **Session continuity:** agent runs should survive restarts and remain inspectable.
- **Skills as operating guidance:** repeatable workflows should be installable and scoped by project, workspace, or runtime.
- **Tool discovery and typed descriptors:** tools should be discoverable as explicit capabilities instead of hidden prompt affordances.
- **Channel flexibility:** the runtime should be usable from CLI first, then UI/API, and later chat or messaging surfaces.

Craik should improve on this pattern by adding:

- structured case files instead of relying on broad transcript state,
- capability receipts for important tool use,
- explicit memory-write policy,
- trust-aware facts,
- contradiction workflows,
- and project-level work graphs.

## What To Borrow From Hermes

Hermes' strongest lessons are about multi-agent coordination.

Reference source:

- Hermes multi-agent orchestration documentation: https://hermes-agent.ai/features/multi-agent

Craik should adopt:

- **Orchestrator plus specialists:** complex work should decompose into role-specific tasks.
- **Isolated worker context:** specialists should receive only task-relevant context.
- **Typed result objects:** workers should return structured outputs that can be validated and routed.
- **Parallel execution:** independent research, review, and implementation tasks should run concurrently where safe.
- **Task boards:** durable task state should outlive a single chat session.
- **Worker heartbeats and blocks:** agents should be able to report progress, get blocked, or request more context.
- **Role profiles:** agents should have explicit responsibilities, tools, and policy boundaries.

Craik should improve on this pattern by making durable memory and governance first-class:

- workers should write handoffs, not just summaries,
- task boards should connect to a work graph,
- specialist outputs should become evidence-bearing artifacts,
- contradictions should become tracked workflow items,
- and orchestration should use Stigmem-backed project memory instead of only orchestrator memory.

## What Craik Adds

Craik's novel surface should be built around features that are difficult to retrofit into prompt-first systems.

### Project Case File

A case file is the task-specific context package assembled before an agent acts.

It includes:

- task objective,
- policy envelope,
- relevant facts,
- relevant ADRs and docs,
- repository state,
- GitHub state,
- recent handoffs,
- stale-risk warnings,
- contradiction warnings,
- and required verification.

### Durable Handoff

A handoff is a machine-readable artifact that lets a future agent continue the work.

It includes:

- what was done,
- what changed,
- what evidence was used,
- commands and tests run,
- facts learned,
- facts invalidated,
- unresolved questions,
- blocked items,
- risks,
- and recommended next steps.

### Capability Receipt

A receipt is a concise record of important runtime action.

Examples:

- file write,
- shell command,
- GitHub write,
- memory write,
- PR creation,
- issue creation,
- fact contradiction,
- approval request,
- approval grant.

### Memory Diff

A memory diff explains how project memory changed during a run.

It should show:

- facts added,
- facts updated,
- facts invalidated,
- contradictions opened,
- contradictions resolved,
- stale facts refreshed,
- and handoffs linked.

### Contradiction Inbox

The contradiction inbox collects incompatible facts or conclusions.

It should support:

- conflict grouping,
- evidence display,
- affected artifact listing,
- reviewer assignment,
- proposed resolution,
- and memory update after resolution.

### Work Graph

The work graph turns chat-like agent runs into durable connected work.

It links:

- tasks,
- agents,
- handoffs,
- facts,
- docs,
- ADRs,
- branches,
- issues,
- PRs,
- commands,
- tests,
- approvals,
- and artifacts.

## Product Differentiation

Craik should be described in terms of durable work, not swarm novelty.

Avoid:

- "agent swarm",
- "autonomous everything",
- "one prompt to replace your team",
- and "memory chatbot".

Prefer:

- durable agent runtime,
- shared project model,
- governed multi-agent work,
- verifiable handoffs,
- capability receipts,
- and memory-native coordination.

## First Audience

The first audience is small engineering teams using coding agents on real repositories.

They already feel the pain:

- agents repeat investigations,
- docs lag implementation,
- chat context disappears,
- multiple agents step on each other,
- handoffs are informal,
- and governance depends on human discipline.

Craik should make those failures visible, structured, and fixable.
