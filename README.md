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

## Agent Integration Model

Craik core is runner-agnostic, but the first implementation should provide direct, first-class runner adapters for:

- Codex
- Claude
- Gemini

Each runner adapter should consume the same Craik contracts: project case file, policy envelope, capability grants, worker result, receipts, handoff, and memory proposals.

OpenClaw is not a required dependency and is not the initial execution target. Craik borrows OpenClaw's useful gateway, workspace, session, tool, and skill ergonomics, while reserving a possible future bridge for teams that want OpenClaw-style channel integrations.

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
- [Differentiators](docs/differentiators.md)
- [Architecture](docs/architecture.md)
- [Runtime Contracts](docs/runtime-contracts.md)
- [Feature Specification](docs/features.md)
- [MVP Plan](docs/mvp.md)
- [Implementation Plan](docs/implementation-plan.md)
- [Roadmap](docs/roadmap.md)
- [Governance Model](docs/governance.md)
- [Stigmem Integration](docs/stigmem-integration.md)
- [Installation](docs/guides/installation.md)
- [Quickstart](docs/guides/quickstart.md)
- [Configuring Craik Home](docs/guides/configuring-craik-home.md)
- [Project Registry](docs/guides/project-registry.md)
- [Development Checks](docs/guides/development.md)
- [CLI Reference](docs/reference/cli.md)
- [Schema Reference](docs/reference/schemas.md)
- [Policy Profiles](docs/reference/policy-profiles.md)
- [Fail-Open](docs/guides/fail-open.md)
- [Capability Grants](docs/guides/capability-grants.md)
- [Redaction](docs/reference/redaction.md)
- [Local State Layout](docs/reference/local-state.md)
- [Local Store](docs/reference/local-store.md)
- [Project Profile](docs/reference/project-profile.md)
- [Secrets](docs/security/secrets.md)
- [Limitations](docs/limitations.md)

## Current Status

Craik is in pre-0.1.0 implementation. The immediate goal is to validate the product shape, define the runtime contracts, and build a narrow MVP around software delivery workflows.

The Python package and `craik` CLI scaffold now exist. Runtime workflows such as project registration, case file assembly, governed execution, receipts, handoffs, and Stigmem-backed memory are still planned work.

The first useful demo should show an agent entering a real repository, assembling the current project model, identifying stale or contradictory documentation, producing a governed plan, and leaving a durable handoff for the next agent.

## Implementation Stack

Craik core will be implemented in Python 3.12+ with a CLI-first package shape. The initial stack is:

- Python 3.12+
- Typer for CLI
- Pydantic for runtime contracts
- SQLite for local persistent state
- `httpx` for Stigmem and GitHub API clients
- `pytest` for tests
- `ruff` and `mypy` for quality gates

TypeScript remains appropriate for future UI, gateway adapters, and OpenClaw-style integrations, but it is not the initial core runtime stack.

## Package and CLI Naming

Craik uses the same name across the public repository, Python package, import module, and CLI command:

- GitHub repository: `Eidetic-Labs/Craik`
- PyPI distribution: `craik`
- Python module: `craik`
- CLI command: `craik`
- Future npm package, if needed: `craik`

Live registry checks on 2026-05-15 showed `craik` available on both PyPI and npm. If a registry race occurs before publication, `craik-runtime` is the fallback distribution name while preserving `craik` as the CLI command and Python module.

## Local State

Craik uses a single product-home directory by default:

```text
~/.craik/
```

The location can be overridden with:

```text
CRAIK_HOME=/custom/path
```

Craik should keep different data classes separated inside that home:

```text
~/.craik/
  config/
  secrets/
  state/
  cache/
  logs/
  receipts/
  handoffs/
  case-files/
  projects/
```

Project-local `.craik/` directories are opt-in only. Craik should not silently create project-local metadata inside repositories.

## License

Craik is released under the [MIT License](LICENSE). The license choice is intended to match the permissive adoption pattern used by comparable agent frameworks while keeping Eidetic Labs trademarks and branding separate from the code license.

## Project Governance

- Contributions: [CONTRIBUTING.md](CONTRIBUTING.md)
- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Security disclosure: [SECURITY.md](SECURITY.md)
- Trademark and brand usage: [TRADEMARKS.md](TRADEMARKS.md)
- Maintainer and release policy: [MAINTAINERS.md](MAINTAINERS.md)

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

## First Demo Target

Craik's first real demo target is Stigmem documentation and state reconciliation.

The demo should:

1. Register the Stigmem repository as a Craik project.
2. Connect to a local Stigmem node.
3. Create a docs reconciliation task.
4. Assemble a case file from repository state, ADRs, public docs, GitHub issues/PRs, recent Stigmem facts, and prior handoffs.
5. Identify stale or contradictory documentation.
6. Produce proposed documentation updates.
7. Record capability receipts for important actions.
8. Generate a durable handoff.
9. Propose or write new Stigmem facts.
10. Export a work graph for the task.

This target is intentionally based on a real workflow that already exposed the need for durable memory, public/internal doc boundaries, ADR constraints, and agent handoffs.
