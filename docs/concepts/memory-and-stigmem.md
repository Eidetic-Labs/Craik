# Memory And Stigmem

Craik treats memory as governed project state, not as an unreviewed transcript
cache.

## Proposal First

Agent-created memory updates become local `craik.memory_proposal` records by
default. Proposals require evidence and remain reviewable before promotion.
Approved local proposals become searchable local facts. Rejected and pending
proposals remain visible for audit.

## Direct Writes

Direct durable memory writes require explicit `memory.write` policy authority.
This applies to local and Stigmem-backed workflows. Without that authority,
Craik should create a proposal and record the reason.

## Stigmem Role

Stigmem is Craik's reference memory and truth substrate. It owns durable facts,
provenance, scopes, trust metadata, contradiction tracking, federation, auth, and
plugin hooks.

Craik owns orchestration, case files, receipts, handoffs, work graphs, policy,
and operator workflows. Craik can run in local degraded mode, but real team
memory should use Stigmem when available.

## Current v0.1.0 Behavior

Craik can:

- detect minimum Stigmem compatibility,
- read facts through the Stigmem HTTP API,
- get fact provenance,
- keep local memory proposals,
- build memory diffs and impact previews,
- deny direct writes without grants,
- and create demo memory proposals.

Case files currently mark missing memory facts as assumptions. Future adapter
work should load relevant Stigmem facts directly into case files.

See [Memory Backends](../reference/memory-backends.md),
[Connecting Stigmem](../guides/connecting-stigmem.md), and
[Stigmem Compatibility](../reference/stigmem-compatibility.md).
