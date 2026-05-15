# Craik

Craik is a durable agent runtime for shared project models and governed multi-agent work.

The project is named after Kenneth Craik, whose work on mental models framed intelligence as the ability to build internal representations of the world and use them to reason before acting. Craik applies that idea to agent systems: agents should not operate as isolated prompt executions. They should work from shared, evidence-backed project models, leave durable handoffs, and act inside explicit governance boundaries.

## Thesis

Most agent frameworks optimize for tool calling, prompt routing, or parallel execution. Those are necessary, but they are not enough for long-running work.

Craik is built around a different premise:

> Agent systems become useful at organizational scale when they can remember, justify, coordinate, dispute, and hand off work over time.

Craik treats memory, provenance, policy, and work state as runtime concerns rather than optional logging.

## Relationship to Stigmem

Craik is a separate product and repository from Stigmem.

- Stigmem is the durable memory and truth substrate: facts, provenance, scopes, trust, federation, auth, and plugin hooks.
- Craik is the agent operating layer: orchestration, context assembly, handoffs, work graphs, capability policy, receipts, and user workflows.

Craik can run in degraded local mode without Stigmem for demos and development, but Stigmem is the reference substrate for real team use.

## Core Ideas

- **Shared project models:** Agents receive a task-specific model of the project before acting.
- **Durable handoffs:** Agent runs end with machine-readable state for the next agent.
- **Fact-grounded context:** Context is assembled from evidence, ADRs, repo state, issues, docs, and memory.
- **Governed execution:** Tool access, write authority, review gates, and documentation obligations are policy-controlled.
- **Capability receipts:** Important actions produce structured records of actor, target, reason, and result.
- **Contradiction handling:** Conflicting facts are surfaced for resolution instead of silently overwritten.
- **Work graph:** Tasks, PRs, issues, facts, decisions, docs, tools, agents, and artifacts are modeled as connected state.

## Planning Docs

- [Vision](docs/vision.md)
- [Product Strategy](docs/product-strategy.md)
- [Architecture](docs/architecture.md)
- [Runtime Contracts](docs/runtime-contracts.md)
- [Feature Specification](docs/features.md)
- [MVP Plan](docs/mvp.md)
- [Implementation Plan](docs/implementation-plan.md)
- [Roadmap](docs/roadmap.md)
- [Governance Model](docs/governance.md)
- [Stigmem Integration](docs/stigmem-integration.md)

## Current Status

Craik is in planning. The immediate goal is to validate the product shape, define the runtime contracts, and build a narrow MVP around software delivery workflows.

The first useful demo should show an agent entering a real repository, assembling the current project model, identifying stale or contradictory documentation, producing a governed plan, and leaving a durable handoff for the next agent.

## Initial Build Target

The first implementation should focus on a repository-aware CLI runtime:

1. Create a project profile for a local Git repository.
2. Connect optional Stigmem memory.
3. Assemble a task case file from repository state, docs, issues, policies, and facts.
4. Execute a governed single-agent task with scoped capabilities.
5. Record capability receipts.
6. Produce a structured handoff.
7. Propose fact updates for future agents.

Multi-agent orchestration, work graph visualization, contradiction inbox, and plugin probation should be layered on after the single-agent durable workflow is working end to end.
