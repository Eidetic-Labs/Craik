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

The local store is the persistence foundation for local and degraded operation. Users who opt out of Stigmem can still keep durable local records for projects, tasks, task runs, receipts, handoffs, memory proposals, assumptions, evidence, and work graph events.

This is not full Stigmem-equivalent shared memory. Local SQLite is single-node state. It does not provide federation, shared team truth, source attestation, or cross-node conflict resolution. The user-facing local memory backend uses local memory proposals and exposes approved proposals as searchable local facts.

## Stored Records

The first migration stores supported v0.1.0 contracts as validated JSON payloads:

| Kind | Contract |
| --- | --- |
| `adjudication_outcomes` | `craik.adjudication_outcome` |
| `projects` | `craik.project_profile` |
| `run_outputs` | `craik.run_output` |
| `tasks` | `craik.task_request` |
| `task_runs` | `craik.task_run` |
| `receipts` | `craik.capability_receipt` |
| `case_files` | `craik.case_file` |
| `contradictions` | `craik.contradiction_report` |
| `context_debt_records` | `craik.context_debt_record` |
| `context_requests` | `craik.context_request` |
| `distilled_instruction_proposals` | `craik.distilled_instruction_proposal` |
| `handoffs` | `craik.handoff` |
| `human_delegations` | `craik.human_delegation_point` |
| `instruction_promotion_reviews` | `craik.instruction_promotion_review` |
| `instruction_provenance` | `craik.instruction_provenance` |
| `instruction_sources` | `craik.instruction_source` |
| `instruction_source_registries` | `craik.instruction_source_registry` |
| `instruction_source_snapshots` | `craik.instruction_source_snapshot` |
| `intent_locks` | `craik.intent_lock` |
| `knowledge_freshness_probes` | `craik.knowledge_freshness_probe` |
| `known_traps` | `craik.known_trap` |
| `proposals` | `craik.memory_proposal` |
| `negative_knowledge` | `craik.negative_knowledge` |
| `promoted_instruction_constraints` | `craik.promoted_instruction_constraint` |
| `red_team_findings` | `craik.red_team_finding` |
| `recovery_sessions` | `craik.recovery_session` |
| `memory_diffs` | `craik.memory_diff` |
| `memory_previews` | `craik.memory_impact_preview` |
| `assumptions` | `craik.assumption` |
| `evidence` | `craik.evidence_reference` |
| `evidence_coverage_scores` | `craik.evidence_coverage_score` |
| `exit_discipline_checks` | `craik.exit_discipline_check` |
| `graph_exports` | `craik.work_graph_export` |
| `graph_events` | `craik.work_graph_event` |
| `handoff_quality_scores` | `craik.handoff_quality_score` |
| `worker_results` | `craik.worker_result` |
| `review_requests` | `craik.review_request` |
| `review_results` | `craik.review_result` |
| `run_deltas` | `craik.run_delta` |
| `runtime_critic_findings` | `craik.runtime_critic_finding` |
| `scratchpad_records` | `craik.scratchpad_record` |
| `tool_result_attestations` | `craik.tool_result_attestation` |
| `unknown_records` | `craik.unknown_record` |
| `scope_change_requests` | `craik.scope_change_request` |
| `scope_change_results` | `craik.scope_change_result` |
| `skill_packages` | `craik.skill_package` |

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

Policy envelope, handoff, and runner links are read from receipt result metadata
keys `policy_envelope_id`, `handoff_ids`, and `runner_metadata`.

## Backup And Cleanup

Back up the SQLite database while Craik is not running, or use SQLite backup tooling once long-running gateway mode exists.

For local cleanup, remove only rebuildable files under `cache/`. Do not delete `state/craik.sqlite3`, `receipts/`, `handoffs/`, or `case-files/` unless you intentionally want to discard local continuity.
