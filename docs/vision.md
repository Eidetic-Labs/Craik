# Vision

Craik exists to make agent work durable.

Current agent tools are improving quickly, but most of them still treat useful state as a side effect of a chat transcript, terminal log, or ad hoc summary. That does not scale to teams, long-lived projects, or multi-agent workflows.

Craik's central claim is that agents need an operating layer that gives them:

- a shared model of the work,
- evidence-backed memory,
- explicit authority boundaries,
- structured handoffs,
- durable artifacts,
- and a way to resolve disagreement.

## Product Category

Craik should not be positioned as another agent framework.

The intended category is:

> Durable agent runtime.

An agent framework helps developers wire agents to tools. A durable agent runtime helps agents participate in long-running work with continuity, accountability, and shared state.

## North Star

A new agent should be able to join a project and understand its current state better than a human who has been away for two weeks.

That includes:

- current goals,
- active branches,
- relevant issues,
- recent PRs,
- architecture constraints,
- immutable ADRs,
- stale docs,
- known risks,
- accepted conventions,
- unresolved questions,
- and facts other agents have learned.

## Design Principles

1. **Memory is not a transcript.**
   Durable memory should be structured, scoped, provenance-aware, and reviewable.

2. **Agents should not silently rewrite reality.**
   Contradictions should become first-class workflow items.

3. **Context should be assembled, not dumped.**
   Agents should receive task-specific case files that explain what matters and why.

4. **Governance belongs in the runtime.**
   Permissions, approvals, policy obligations, and receipts should be part of normal execution.

5. **Handoffs are artifacts.**
   A final chat message is not enough. Agent work should leave structured state for future agents.

6. **Local mode should exist, but not define the product.**
   Craik should be easy to try without Stigmem, while making clear that durable multi-agent work needs a real memory substrate.

## Initial Wedge

The first market wedge is multi-agent software delivery for small technical teams.

This wedge is concrete enough to prove the runtime:

- repositories have history,
- ADRs and docs go stale,
- CI and PRs create verifiable artifacts,
- issues encode work,
- agents need context,
- and handoffs matter.

If Craik works here, it can expand into incident response, research operations, compliance workflows, support engineering, and other long-running knowledge work.
