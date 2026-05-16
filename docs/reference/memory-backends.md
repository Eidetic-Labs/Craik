# Memory Backends

Craik memory backends expose a small proposal-first interface.

Required behavior:

- create reviewable memory proposals,
- list proposals by task or status,
- approve proposals,
- reject proposals,
- search approved local facts,
- and require evidence before promotion.

## Backends

### Ephemeral

`EphemeralMemoryStore` keeps proposals in process memory. It is intended for tests and short demos.

### Local

`LocalMemoryStore` persists `craik.memory_proposal` records in the local SQLite store.

Approved local proposals are searchable as local facts. Rejected and pending proposals remain visible for audit but are not returned by fact search.

Direct local memory writes are denied until a policy-granted write path exists. Proposal creation is the default path.

## Proposal Status

`craik.memory_proposal` records use these statuses:

- `pending`
- `approved`
- `rejected`

Approval records reviewer identity, decision reason, and decision timestamp.
