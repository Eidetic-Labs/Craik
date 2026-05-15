# MVP Plan

The MVP should prove one complete workflow instead of building a broad platform shell.

## MVP Goal

Given a real software repository, Craik should assemble a task-specific project model, guide an agent through governed work, record capability receipts, and produce a durable handoff backed by memory.

## Primary Demo

1. Connect Craik to a GitHub repository.
2. Ingest current repo state, docs, ADRs, issues, PRs, branch status, and recent Stigmem facts.
3. Ask Craik to review whether documentation matches implementation state.
4. Craik assembles a case file.
5. An agent performs the review with scoped read/write capabilities.
6. Craik records key tool-use receipts.
7. The agent proposes doc updates and facts.
8. Craik surfaces any contradictions or stale assumptions.
9. The user approves changes.
10. Craik creates a structured handoff and updates memory.

## MVP Components

### CLI

Commands:

- `craik init`
- `craik connect stigmem`
- `craik project add`
- `craik task create`
- `craik task run`
- `craik handoff show`
- `craik facts propose`
- `craik receipts list`

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
