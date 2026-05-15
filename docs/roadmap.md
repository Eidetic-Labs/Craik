# Roadmap

This roadmap is intentionally staged around evidence. Craik should only broaden after the runtime proves durable value in real work.

## Phase 0: Product Foundation

Goals:

- finalize product thesis,
- define initial schemas,
- choose implementation language and package shape,
- publish the MIT license,
- publish lightweight contribution, conduct, security, trademark, and maintainer policies,
- document relationship to Stigmem,
- define local degraded mode,
- define Stigmem-backed full mode,
- and create the first working CLI skeleton.

Exit criteria:

- MIT license committed,
- initial governance files committed,
- schemas committed,
- local task creation works,
- handoff schema validated,
- and Stigmem connection can read/write basic facts.

Maps to implementation milestones:

- Milestone 1: Contract Foundation.
- Milestone 2: Project Registry And Local State.

## Phase 1: Repository-Aware Runtime

Goals:

- connect to local repositories,
- inspect branch and diff state,
- assemble case files from repo docs and policies,
- run read-only review tasks,
- record capability receipts,
- and produce durable handoffs.

Exit criteria:

- agent can review a real repo and leave a reusable handoff,
- receipts capture important actions,
- case file assembly is deterministic enough to test,
- and docs explain degraded vs Stigmem-backed modes.

Maps to implementation milestones:

- Milestone 3: Case File Assembly.
- Milestone 4: Policy And Receipts.
- Milestone 5: Handoff Loop.

## Phase 2: GitHub Workflows

Goals:

- add GitHub issue and PR context,
- connect task state to issues and PRs,
- read CI state,
- comment with handoffs or review results,
- and optionally open PRs under policy.

Exit criteria:

- agent can connect repo work to GitHub state,
- handoffs link to issues and PRs,
- verification status is visible,
- and policy controls write operations.

Maps to implementation milestones:

- Milestone 7: GitHub Adapter.

## Phase 3: Multi-Agent Coordination

Goals:

- support orchestrator and specialist roles,
- support parallel read-only investigations,
- support review and adjudication roles,
- support contradiction reports,
- and update the work graph from multiple agents.

Exit criteria:

- multiple agents can work without overwriting each other's context,
- disagreements are surfaced,
- handoffs preserve specialist outputs,
- and the work graph shows task lineage.

Maps to implementation milestones:

- Milestone 10: Multi-Agent Orchestration.

## Phase 4: Governance-Native Execution

Goals:

- implement policy envelopes,
- define capability grants,
- require approvals for risky actions,
- record structured receipts,
- support context contracts,
- and enforce memory-write rules.

Exit criteria:

- agents act through explicit capability grants,
- operator approvals are captured,
- policy violations are blocked or flagged,
- and receipt logs can explain important changes.

Maps to implementation milestones:

- Milestone 4: Policy And Receipts.
- Milestone 11: Skills And Probationary Plugins.

## Phase 5: Stigmem-Native Intelligence

Goals:

- use Stigmem trust tiers,
- use contradiction tracking,
- write scoped facts,
- detect stale facts,
- generate memory diffs,
- and support fact review workflows.

Exit criteria:

- Craik can explain what memory changed during a run,
- contradictions become actionable work items,
- stale-risk facts are surfaced before acting,
- and future agents consume prior facts reliably.

Maps to implementation milestones:

- Milestone 6: Stigmem Backend.
- Milestone 9: Contradictions And Memory Diff.

## Phase 6: Operator Experience

Goals:

- build dashboard views,
- expose work graph navigation,
- show handoff history,
- show receipts,
- show contradiction inbox,
- and make project status inspectable.

Exit criteria:

- users can understand what agents did without reading raw logs,
- handoffs are easy to browse,
- and project state is visible at a glance.

Maps to implementation milestones:

- Milestone 8: Work Graph.
- Later UI milestones after CLI validation.

## Phase 7: Plugin And Ecosystem Layer

Goals:

- define Craik plugin contracts,
- support probationary plugins,
- support adapter packages,
- support skill creation workflows,
- and publish reference integrations.

Exit criteria:

- external integrations can be added without modifying core runtime,
- plugin capabilities are governed,
- and plugin behavior leaves receipts.
