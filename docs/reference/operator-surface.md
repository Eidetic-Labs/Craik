# Operator Surface

Craik has read-only operator view contracts and formatter helpers. A complete TUI
or dashboard is post-MVP scope; see [Post-MVP Scope](post-mvp-scope.md).

## Decision

The first operator inspection work is terminal-friendly formatting backed by
local-store queries and validated contracts.

A full TUI remains a later option because the formatter-first path:

- works in the same terminal where agents and operators already run Craik;
- can inspect local SQLite state without starting a service;
- keeps read-only review workflows simple;
- avoids adding browser, server, authentication, and asset concerns before the
  operator views are proven;
- can reuse the same formatter contracts that future dashboard views may call.

## Boundary

The v0.7.0 operator surface is read-only by default. It may display state from
the local store, docs, fixtures, and validated contracts. It must not mutate
memory, approve grants, resolve contradictions, delete records, or execute
plugins without an explicit future command and policy boundary.

## Preview Navigation

Future TUI or dashboard work should organize views around operator questions:

- `Overview`: project, active tasks, recent handoffs, and blocked states;
- `Work Graph`: graph events, exports, dependencies, and verification links;
- `Handoffs`: summaries, next steps, receipts, evidence, and risks;
- `Receipts`: capability and plugin action records;
- `Inbox`: contradictions, delegations, and context requests;
- `Evidence`: evidence references, assumptions, and memory impact previews;
- `Quality`: quality scores, critic findings, red-team findings, and gates;
- `Instructions`: sources, snapshots, distilled proposals, and reviews;
- `Traps`: known traps and negative knowledge;
- `Run Deltas`: recovery and continuity changes.

Each view should degrade cleanly when records are missing. Missing data should be
shown as unavailable state, not inferred.

## Data Sources

The initial surface should read from existing contracts and store helpers:

- [`craik.handoff`](schemas.md);
- [`craik.capability_receipt`](schemas.md);
- [`craik.plugin_receipt`](schemas.md);
- [`craik.work_graph_event`](schemas.md);
- [`craik.contradiction_report`](schemas.md);
- [`craik.evidence_reference`](schemas.md);
- [`craik.assumption`](schemas.md);
- [`craik.memory_impact_preview`](schemas.md);
- [`craik.human_delegation_point`](schemas.md);
- [`craik.context_request`](schemas.md);
- [`craik.handoff_quality_score`](schemas.md);
- [`craik.evidence_coverage_score`](schemas.md);
- [`craik.runtime_critic_finding`](schemas.md);
- [`craik.red_team_finding`](schemas.md);
- [`craik.instruction_source`](schemas.md);
- [`craik.distilled_instruction_proposal`](schemas.md);
- [`craik.known_trap`](schemas.md);
- [`craik.negative_knowledge`](schemas.md);
- [`craik.run_delta`](schemas.md).

## Follow-On Views

Post-MVP work can add these views incrementally behind the same read-only
boundary. Each view should have focused tests for formatting, empty-state
behavior, and links to the underlying contracts before it is described as
operational.
