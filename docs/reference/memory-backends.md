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

### Stigmem

`StigmemMemoryStore` uses the Stigmem HTTP API for shared durable memory and keeps proposals in Craik local state. Stigmem facts are immutable assertions, so Craik still uses local proposals until a proposal is approved and policy grants a direct write.

The minimum endpoint mapping is:

- `GET /healthz`
- `GET /.well-known/stigmem`
- `POST /v1/facts`
- `GET /v1/facts`
- `GET /v1/facts/{fact_id}`
- `GET /v1/facts/{fact_id}/provenance`

Use `craik connect stigmem` to detect compatibility. Configure the node with `CRAIK_STIGMEM_URL` and authenticated nodes with `CRAIK_STIGMEM_API_KEY`.

## Proposal Status

`craik.memory_proposal` records use these statuses:

- `pending`
- `approved`
- `rejected`

Approval records reviewer identity, decision reason, and decision timestamp.

## Diff And Preview

`craik.memory_diff` explains task-scoped memory activity: proposals created, proposals approved or rejected, facts written, write failures, and facts read.

`craik.memory_impact_preview` shows the expected impact before promotion or direct writes: facts to add, facts to invalidate, likely contradictions, missing evidence, and scope counts.

Use:

```sh
craik memory diff <task-id>
craik memory preview <task-id>
```
