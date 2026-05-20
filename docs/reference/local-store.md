# Local store

<p className="craik-meta"><span>4 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The SQLite-backed local persistence layer — paths, stored records,
migrations, secret-handling, receipt queries, and backup/cleanup
practice.

</div>

<div className="craik-keypoint">

**Local SQLite is single-node state.**

Useful for local and degraded operation. It is not Stigmem-equivalent
shared memory — no federation, shared team truth, source attestation,
or cross-node conflict resolution.

</div>

## Paths

<div className="craik-fields">

<div>
<dt>Variable</dt>
<dt><span className="craik-fields__type">Default</span></dt>
<dd>Database path</dd>
</div>

<div>
<dt>Default</dt>
<dt><span className="craik-fields__type">no override</span></dt>
<dd><code>~/.craik/state/craik.sqlite3</code></dd>
</div>

<div>
<dt><code>CRAIK_HOME</code></dt>
<dt><span className="craik-fields__type">override</span></dt>
<dd><code>$CRAIK_HOME/state/craik.sqlite3</code></dd>
</div>

</div>

## Stored records

The first migration stores supported v0.1.0 contracts as validated
JSON payloads.

| Kind | Contract |
| --- | --- |
| `adjudication_outcomes` | `craik.adjudication_outcome` |
| `adapter_packages` | `craik.adapter_package` |
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
| `plugin_capability_grants` | `craik.plugin_capability_grant` |
| `plugin_descriptors` | `craik.plugin_descriptor` |
| `plugin_probations` | `craik.plugin_probation` |
| `plugin_receipts` | `craik.plugin_receipt` |
| `proposals` | `craik.memory_proposal` |
| `negative_knowledge` | `craik.negative_knowledge` |
| `promoted_instruction_constraints` | `craik.promoted_instruction_constraint` |
| `reference_integrations` | `craik.reference_integration` |
| `red_team_findings` | `craik.red_team_finding` |
| `recovery_sessions` | `craik.recovery_session` |
| `memory_diffs` | `craik.memory_diff` |
| `memory_previews` | `craik.memory_impact_preview` |
| `assumptions` | `craik.assumption` |
| `evidence` | `craik.evidence_reference` |
| `evidence_coverage_scores` | `craik.evidence_coverage_score` |
| `exit_discipline_checks` | `craik.exit_discipline_check` |
| `gateway_configs` | `craik.gateway_config` |
| `gateway_runtime_states` | `craik.gateway_runtime_state` |
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
| `skill_invocation_contexts` | `craik.skill_invocation_context` |
| `skill_packages` | `craik.skill_package` |
| `skill_registries` | `craik.skill_registry` |

Every stored payload is validated through the Pydantic contract
registry **before persistence and again when loaded**.

## Migrations

Craik tracks migration state through SQLite `PRAGMA user_version` and
the `migrations` table. Migrations run through a registered,
forward-only migration runner. Migration `2` adds
`local_store_metadata` so diagnostics can distinguish the store schema
version from the package version. Migration `3` records that the store
was upgraded through the registered migration framework.

<div className="craik-grid">

<div><h4>Deterministic</h4><p>Migrations must be deterministic.</p></div>
<div><h4>New kinds require tests + docs</h4></div>
<div><h4>Newer DB versions fail clearly</h4></div>
<div><h4>Corrupt DBs raise an error</h4><p>Never silently recreated.</p></div>

</div>

See [Local store migrations](../guides/local-store-migrations.md) for
fixture compatibility and recovery guidance.

## Secrets

<div className="craik-keypoint">

**No unredacted secrets persist.**

Payloads are checked with the central redaction utility before
persistence and rejected if they still appear to contain secret
material.

</div>

## Receipt queries

The receipt store builds on local SQLite persistence for
`craik.capability_receipt` records.

<div className="craik-grid">

<div><h4>All receipts</h4></div>
<div><h4>One receipt by id</h4></div>
<div><h4>Receipts by task id</h4></div>
<div><h4>Receipts linked to a policy envelope id</h4></div>
<div><h4>Receipts linked to a handoff id</h4></div>

</div>

Policy envelope, handoff, and runner links are read from receipt
result metadata keys `policy_envelope_id`, `handoff_ids`, and
`runner_metadata`.

## Backup and cleanup

Back up the SQLite database while Craik is not running, or use SQLite
backup tooling once long-running gateway mode exists.

For local cleanup, remove only rebuildable files under `cache/`.
**Do not delete** `state/craik.sqlite3`, `receipts/`, `handoffs/`, or
`case-files/` unless you intentionally want to discard local
continuity.

## What's next

<div className="craik-next">

<a href="../../guides/local-store-migrations/">
<strong>Guide</strong>
<span>Local store migrations</span>
<small>Recovery from failed migrations.</small>
</a>

<a href="../schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The contracts these tables persist.</small>
</a>

<a href="../redaction/">
<strong>Reference</strong>
<span>Redaction</span>
<small>The boundary that keeps secrets out of the store.</small>
</a>

</div>
