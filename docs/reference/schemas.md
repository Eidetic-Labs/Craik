# Schema Reference

Craik runtime contracts are strict Pydantic models. Persisted contracts include:

```json
{
  "schema": "craik.<contract-name>",
  "version": "0.1.0"
}
```

The `schema` value identifies the contract type. The `version` value identifies the contract version. Unknown fields are rejected so adapters, memory backends, and future plugins do not silently depend on accidental payload shape.

## Inspecting Schemas

List registered schemas:

```sh
craik schema list
```

Print JSON Schema for one contract:

```sh
craik schema show craik.task_request
```

## v0.1.0 Contracts

| Schema | Purpose |
| --- | --- |
| `craik.agent_onboarding` | Summarizes runner-readable project context before an agent starts work. |
| `craik.assumption` | Tracks unresolved assumptions that need evidence before promotion to fact. |
| `craik.capability_grant` | Defines scoped permission for an action family. |
| `craik.capability_receipt` | Records an auditable action result under a policy profile. |
| `craik.case_file` | Captures task-specific context assembled before execution. |
| `craik.compiled_prompt` | Captures a deterministic policy-aware runner prompt. |
| `craik.contradiction_report` | Captures incompatible assertions for review. |
| `craik.evidence_reference` | Points to source material supporting a contract assertion. |
| `craik.handoff` | Summarizes durable run state for future agents. |
| `craik.intent_lock` | Preserves task intent and scope boundaries. |
| `craik.memory_backend_capabilities` | Records detected memory backend support. |
| `craik.memory_diff` | Explains run-scoped memory reads, proposals, writes, and failures. |
| `craik.memory_impact_preview` | Previews memory additions, invalidations, evidence gaps, and likely contradictions. |
| `craik.memory_proposal` | Describes reviewable memory updates. |
| `craik.policy_envelope` | Defines runtime authority and obligations. |
| `craik.project_profile` | Defines a project Craik can reason about. |
| `craik.runner_adapter_request` | Defines normalized input handed to a runner adapter. |
| `craik.runner_adapter_result` | Defines normalized output returned by a runner adapter. |
| `craik.runner_capability_matrix` | Defines runner capability support, trust boundary, and default grant posture. |
| `craik.runner_metadata` | Defines stable runner identity, mode, and capability summary. |
| `craik.task_run` | Tracks durable single-agent run status, phase, linked artifacts, receipts, and handoff. |
| `craik.task_request` | Defines requested work. |
| `craik.work_graph_export` | Exports connected graph nodes and edges. |
| `craik.work_graph_event` | Updates the work graph. |

## Examples

Fixture examples for every v0.1.0 contract live in:

```text
tests/fixtures/contracts/v0_1/contracts.json
```

Those fixtures are loaded by tests, validated against the registered Pydantic models, and round-tripped through JSON.

## Versioning And Migration

The first contract version is `0.1.0`.

Rules:

- Compatible field additions require tests, docs, and fixture updates.
- Breaking changes require a new schema version and migration notes.
- Runtime code should reject unknown fields by default.
- Durable memory writes should preserve source, confidence, scope, and trust metadata.
- Policy and receipt contracts should preserve profile, fail-open, redaction, and approval metadata.
- Adapter-produced receipts and handoffs should preserve stable runner metadata while keeping provider-specific details nested and redacted.
