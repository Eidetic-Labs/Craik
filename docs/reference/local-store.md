# Local Store

Craik uses SQLite for local runtime persistence.

Default database path:

```text
~/.craik/state/craik.sqlite3
```

With `CRAIK_HOME`:

```text
$CRAIK_HOME/state/craik.sqlite3
```

The local store is the persistence foundation for local and degraded operation. Users who opt out of Stigmem can still keep durable local records for projects, tasks, receipts, handoffs, memory proposals, assumptions, evidence, and work graph events.

This is not full Stigmem-equivalent shared memory. Local SQLite is single-node state. It does not provide federation, shared team truth, source attestation, or cross-node conflict resolution. The user-facing local memory backend is implemented separately from this storage substrate.

## Stored Records

The first migration stores supported v0.1.0 contracts as validated JSON payloads:

| Kind | Contract |
| --- | --- |
| `projects` | `craik.project_profile` |
| `tasks` | `craik.task_request` |
| `receipts` | `craik.capability_receipt` |
| `case_files` | `craik.case_file` |
| `handoffs` | `craik.handoff` |
| `proposals` | `craik.memory_proposal` |
| `assumptions` | `craik.assumption` |
| `evidence` | `craik.evidence_reference` |
| `graph_events` | `craik.work_graph_event` |

Every stored payload is validated through the Pydantic contract registry before persistence and again when loaded.

## Migrations

Craik tracks the local store migration through SQLite `PRAGMA user_version`.

Rules:

- migrations must be deterministic,
- new stored contract kinds require tests and docs,
- newer unsupported database versions should fail clearly,
- and corrupt or unreadable databases should raise a local store error instead of being silently recreated.

## Secrets

The local store must not persist unredacted secrets. Payloads are checked with the central redaction utility before persistence and rejected if they still appear to contain secret material.

## Receipt Queries

The receipt store builds on local SQLite persistence for `craik.capability_receipt` records.

Supported lookup paths:

- all receipts,
- one receipt by id,
- receipts by task id,
- receipts linked to a policy envelope id,
- and receipts linked to a handoff id.

Policy envelope and handoff links are read from receipt result metadata keys `policy_envelope_id` and `handoff_ids`.

## Backup And Cleanup

Back up the SQLite database while Craik is not running, or use SQLite backup tooling once long-running gateway mode exists.

For local cleanup, remove only rebuildable files under `cache/`. Do not delete `state/craik.sqlite3`, `receipts/`, `handoffs/`, or `case-files/` unless you intentionally want to discard local continuity.
