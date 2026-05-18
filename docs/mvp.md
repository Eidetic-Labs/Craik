# MVP Plan

The MVP should prove one complete workflow instead of building a broad platform shell.

## MVP Goal

Given a real software repository, Craik should assemble a task-specific project model, guide an agent through governed work, record capability receipts, and produce a durable handoff backed by memory.

## Accepted Primary Demo

The accepted first demo target is Stigmem documentation and state reconciliation.

1. Connect Craik to a GitHub repository.
2. Register the Stigmem repository as the project.
3. Connect to a local Stigmem node.
4. Authenticate the operator via OIDC and configure a provider credential profile.
5. Ingest current repo state, docs, ADRs, issues, PRs, branch status, prior handoffs, and recent Stigmem facts.
6. Ask Craik to review whether documentation matches implementation state.
7. Craik assembles a case file.
8. An agent performs the review with scoped read/write capabilities.
9. Craik records key tool-use receipts.
10. The agent proposes doc updates and facts.
11. Craik surfaces any contradictions or stale assumptions.
12. The user approves changes.
13. Craik creates a structured handoff, updates memory, and exports the work graph.

This demo is the first proof point because it exercises the problems Craik is designed to solve:

- stale documentation,
- public/internal documentation boundaries,
- immutable ADR constraints,
- live GitHub state,
- Stigmem facts,
- operator and credential identity,
- multi-agent handoff continuity,
- and verifiable tool use.

## MVP Components

The MVP should be delivered as a CLI-first runtime with real persisted state and typed schemas. A UI should wait until the CLI workflow proves that the runtime contracts are correct.

### CLI

Commands:

- `craik home init`
- `craik connect stigmem`
- `craik login`
- `craik logout`
- `craik whoami`
- `craik auth list`
- `craik auth add`
- `craik auth remove`
- `craik auth test`
- `craik auth status`
- `craik auth approve`
- `craik auth grant`
- `craik project add`
- `craik task create`
- `craik case build`
- `craik run execute`
- `craik handoff show`
- `craik handoff create`
- `craik memory propose`
- `craik memory diff`
- `craik receipts list`

The command list should start small. Implementation should prioritize:

1. `craik home init`
2. `craik project add`
3. `craik login` and `craik auth add`
4. `craik task create`
5. `craik case build`
6. `craik run execute`
7. `craik receipts list`
8. `craik handoff create`
9. `craik memory diff`

### Runtime Schemas

Required schemas:

- task request,
- project profile,
- case file,
- capability grant,
- capability receipt,
- handoff,
- memory proposal,
- contradiction report,
- verification result.

### Memory Backends

Required:

- in-memory backend for tests,
- local file backend for development,
- Stigmem backend for full product behavior.

### Authentication

Required:

- typed credential profiles in `auth-profiles.json`;
- credential source kinds: env-var API key, local-CLI OAuth fallback,
  vendor-CLI bridge, external secret reference, Stigmem-backed credential
  reference, and marker identity for local no-secret providers;
- credential pool with rotation, failover, and per-profile health tracking;
- OIDC operator login with session persistence;
- workload identity providers for CI, Kubernetes, generic file tokens, and
  env-var tokens;
- RFC 8693 token exchange for short-lived federated provider credentials;
- credential-scoped receipts;
- operator-scoped receipts;
- policy-bound operators and credentials;
- approval-gated first live credential use.

### GitHub Adapter

Required reads:

- repository metadata,
- branches,
- issues,
- pull requests,
- changed files,
- comments,
- CI status.

Initial writes:

- create issue,
- create PR,
- comment on issue or PR.

### Repository Adapter

Required:

- read file tree,
- read files,
- inspect branch status,
- inspect diffs,
- run configured validation commands,
- write patches through an explicit grant.

### Handoff Writer

Required sections:

- task summary,
- completed actions,
- artifacts created,
- files changed,
- commands run,
- tests run,
- facts learned,
- facts invalidated,
- unresolved questions,
- risks,
- next steps,
- and links to receipts.

### Case File Assembler

Required sections:

- task objective,
- policy envelope,
- relevant facts,
- relevant docs,
- relevant ADRs,
- current branch state,
- open issues and PRs,
- recent handoffs,
- stale-risk notes,
- contradiction notes,
- verification expectations.

The case file is the most important MVP artifact. If a future agent cannot use it to understand why the current task is safe, relevant, and bounded, the MVP is not complete.

## MVP Build Order

1. Define schemas and fixtures.
2. Build local project registry.
3. Build case file assembly from local repo state.
4. Add local receipt and handoff storage.
5. Add policy envelope enforcement for write boundaries.
6. Add Stigmem memory read/propose/write.
7. Add GitHub read-only context.
8. Add guarded GitHub writes.
9. Add work graph export.
10. Add contradiction reports and memory diff.

## Non-Goals For MVP

- Full UI.
- Plugin marketplace.
- Multi-tenant SaaS.
- Autonomous background execution.
- Broad model-provider abstraction.
- Complex scheduling.
- Enterprise policy editor.
- Federated memory.

## MVP Success Criteria

The MVP succeeds if a new agent can:

- understand the current state of a repository faster,
- avoid repeating already-resolved investigation,
- identify stale documentation,
- leave a useful handoff,
- and create memory updates that future agents can use.

The MVP should be evaluated on real project workflows, not toy examples.

For the accepted Stigmem docs reconciliation demo, success also requires:

- the case file clearly identifies ADR constraints and public/internal documentation boundaries,
- stale documentation findings include evidence,
- proposed updates avoid immutable ADR edits,
- receipts capture meaningful file, shell, GitHub, and memory actions,
- the handoff is useful to a later agent without relying on chat history,
- and Stigmem receives appropriate fact proposals or fact writes.
