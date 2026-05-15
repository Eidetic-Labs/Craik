# Stigmem Integration

Craik should use Stigmem as its reference memory and truth substrate.

## Boundary

Stigmem owns:

- facts,
- provenance,
- scopes,
- trust metadata,
- contradiction tracking,
- federation,
- auth,
- and memory plugin hooks.

Craik owns:

- task orchestration,
- project case files,
- agent role assignment,
- capability grants,
- receipts,
- handoffs,
- work graph state,
- and operator workflows.

## Memory Store Interface

Craik should define a memory store interface based on capabilities.

Required base capabilities:

- read facts,
- propose facts,
- write facts,
- search facts,
- list facts by entity,
- attach provenance,
- and record handoff references.

Advanced capabilities:

- contradiction detection,
- trust tiers,
- scoped visibility,
- memory diff,
- fact expiration or stale-risk markers,
- and federation.

## Minimum Compatibility Target

Craik's first Stigmem backend should target the current Stigmem HTTP API shape exposed by the reference node.

Required endpoints:

- `GET /healthz`
- `GET /.well-known/stigmem`
- `POST /v1/facts`
- `GET /v1/facts`
- `GET /v1/facts/{fact_id}`
- `GET /v1/facts/{fact_id}/provenance`

Required auth behavior:

- support bearer API keys through `Authorization: Bearer <key>`,
- detect whether auth is required from `/.well-known/stigmem`,
- surface `401` and `403` as configuration or permission errors,
- and never log raw API keys.

Required fact model fields:

- `id`,
- `entity`,
- `relation`,
- `value`,
- `source`,
- `timestamp`,
- `confidence`,
- `scope`.

Required assertion fields:

- `entity`,
- `relation`,
- `value`,
- `source`,
- `confidence`,
- `scope`,
- optional `valid_until`,
- optional `garden_id`,
- optional `attestation`.

Required query filters:

- `entity`,
- `relation`,
- `source`,
- `scope`,
- `min_confidence`,
- `include_contradicted`,
- `include_expired`,
- `after`,
- `cursor`,
- `limit`.

Required scopes:

- `local`,
- `team`,
- `company`,
- `public`.

Craik should not require federation, gardens, source attestation, quarantine, tombstones, vector recall, or plugins for its first backend. It may use them when advertised or available.

## Endpoint Mapping

| Craik memory method | Stigmem endpoint | Required | Notes |
| --- | --- | --- | --- |
| `health()` | `GET /healthz` | Yes | Confirms node is reachable. |
| `discover()` | `GET /.well-known/stigmem` | Yes | Reads node id, node URL, auth mode, federation, source attestation, namespaces. |
| `write_fact(fact)` | `POST /v1/facts` | Yes | Used only when policy grants direct memory write. |
| `propose_fact(proposal)` | Local Craik store, optional later Stigmem fact | Yes | Stigmem has immutable facts, not a generic proposal queue; Craik keeps proposals locally until approved. |
| `search_facts(query, scope)` | Prefer `POST /v1/recall`; fallback to `GET /v1/facts` | Optional recall, required fallback | Recall gives ranked results; query endpoint is the minimum reliable path. |
| `list_facts(entity, relation, scope)` | `GET /v1/facts` | Yes | Use pagination with `cursor` and `limit`. |
| `get_fact(fact_id)` | `GET /v1/facts/{fact_id}` | Yes | Supports UUID or CID where node supports CID addressing. |
| `get_provenance(fact_id)` | `GET /v1/facts/{fact_id}/provenance` | Yes | Used to populate evidence and case files. |
| `list_contradictions()` | `GET /v1/conflicts` | Optional | Use if available; otherwise use local contradiction reports. |
| `resolve_contradiction()` | `POST /v1/conflicts/{conflict_id}/resolve` | Optional | Craik should require explicit memory-write grant. |
| `memory_diff(run_id)` | Craik local store | Yes | Stigmem does not provide run-scoped memory diffs; Craik computes from its proposals/writes. |

## Capability Detection

The Stigmem backend should perform capability detection at connect time.

Required checks:

1. `GET /healthz` returns success.
2. `GET /.well-known/stigmem` returns metadata.
3. If auth is required, authenticated `GET /v1/facts?limit=1` succeeds.
4. If writes are configured, a dry-run is not available; Craik should validate permissions by policy and surface first write failure clearly.

Optional checks:

- `POST /v1/recall` availability,
- `GET /v1/conflicts` availability,
- `GET /v1/auth/keys` availability for key inspection,
- `GET /v1/facts/{fact_id}/provenance` availability,
- source-attestation mode from well-known metadata,
- federation status from well-known metadata.

Detected capabilities should be stored in Craik local state and included in case files when relevant.

## Fact Mapping

Craik fact proposals map to Stigmem assertions as follows:

| Craik field | Stigmem field |
| --- | --- |
| `entity` | `entity` |
| `relation` | `relation` |
| `value` | `value` |
| `source` | `source` |
| `confidence` | `confidence` |
| `scope` | `scope` |
| `expires_at` | `valid_until` |
| `garden_id` | `garden_id` |
| `attestation` | `attestation` |

Craik should use stable relation namespaces and avoid the reserved `stigmem:` relation prefix for ordinary product facts.

Recommended Craik relation prefixes:

- `craik:task:*`
- `craik:handoff:*`
- `craik:receipt:*`
- `craik:docs:*`
- `craik:policy:*`
- `codex:*` only for facts written by Codex-specific automation or compatibility with existing team facts.

## Source And Identity

Craik should write facts with an explicit source identity.

Recommended source forms:

- `agent:craik`
- `agent:craik:<runner>`
- `agent:craik:<runner>:<stable-agent-id>`
- `user:<id>` when the human is the source of the assertion.

If Stigmem source attestation is in `enforce` mode, Craik must either:

- set `source` to the authenticated entity URI,
- or attach a valid Stigmem agent-key attestation.

If source attestation is in `warn` mode, Craik should surface warnings in receipts and handoffs.

## Local Proposal Model

Craik should not treat every proposed fact as an immediate Stigmem write.

Default behavior:

- agent-created facts become local memory proposals,
- direct Stigmem writes require a memory write grant,
- user approval can promote proposals to Stigmem facts,
- rejected proposals stay local for audit unless retention policy removes them.

This preserves Craik's strict-by-default posture while still using Stigmem as the durable truth substrate.

## Contradiction Strategy

Stigmem exposes conflicts when facts with the same entity, relation, and scope disagree.

Craik should use Stigmem conflicts when available:

- list open conflicts with `GET /v1/conflicts?status=unresolved`,
- link conflict facts into case files,
- require explicit memory-write grant before resolving with `POST /v1/conflicts/{conflict_id}/resolve`.

Craik should also keep local contradiction reports because not all Craik contradictions are Stigmem-level conflicts. Examples:

- documentation says a task is planned while GitHub shows it merged,
- public docs contain internal-only implementation labels,
- a handoff contradicts a later branch state,
- a runner result conflicts with a verifier result.

Local contradiction reports may later produce Stigmem fact proposals.

## Memory Diff Strategy

Craik owns run-scoped memory diffs.

A memory diff should include:

- local proposals created,
- proposals approved,
- Stigmem facts written,
- Stigmem write failures,
- facts read into the case file,
- contradictions opened,
- contradictions resolved,
- and handoff summary facts written.

Stigmem facts should be referenced by `id` and `cid` when available.

## Error Mapping

Craik should map Stigmem errors into actionable backend errors.

| HTTP status | Craik meaning |
| --- | --- |
| `400` | invalid request or unsupported query shape |
| `401` | missing or invalid API key |
| `403` | insufficient Stigmem permission |
| `404` | missing fact, endpoint, or tombstone-hidden fact |
| `409` | duplicate or already-resolved lifecycle conflict |
| `422` | schema validation failure |
| `5xx` | node unavailable or internal node error |

Error messages must be redacted before they are persisted in receipts, logs, handoffs, or case files.

## Stigmem Fact Usage

Craik should use Stigmem facts to assemble case files.

Relevant fact types:

- repo current state,
- branch and PR status,
- docs policy,
- ADR policy,
- implementation decisions,
- known gaps,
- stale-risk docs,
- agent handoffs,
- capability constraints,
- and project-specific conventions.

## Stigmem Fact Writes

Craik should write facts when agents learn reusable project state.

Examples:

- a doc policy that future agents must respect,
- a recurring validation command,
- an implementation constraint,
- a repository convention,
- a stale documentation warning,
- a completed migration status,
- or a contradiction that needs resolution.

## Handoff Storage

Craik should store handoffs as structured artifacts and write summary facts to Stigmem.

The full handoff may live in Craik storage or the repository. Stigmem should receive enough metadata for discovery:

- task id,
- repository,
- branch,
- agent identity,
- summary,
- changed artifacts,
- facts learned,
- unresolved questions,
- and handoff URI.

## Local Development

Craik should support a local memory backend for development and tests.

This should not become an alternate product thesis. The local backend exists to lower setup friction and make tests deterministic. Stigmem remains the production-grade reference backend.
