# Runtime Contracts

Craik should be built around stable, versioned contracts. The contracts are the product spine: adapters, agents, memory backends, and future plugins should integrate through them.

Contract examples below use JSON-like shapes for clarity. The final implementation should define them as typed schemas with validation.

## Versioning

Every persisted contract should include:

```json
{
  "schema": "craik.<contract-name>",
  "version": "0.1.0"
}
```

Breaking changes require a new version and migration path.

## Task Request

Defines work requested by a user, system, or another agent.

```json
{
  "schema": "craik.task_request",
  "version": "0.1.0",
  "id": "task_...",
  "title": "Review documentation against implementation state",
  "objective": "Find stale docs and propose updates.",
  "project_id": "project_...",
  "requested_by": "user:...",
  "priority": "normal",
  "mode": "plan|review|implement|verify",
  "constraints": ["Do not edit ADRs."],
  "expected_outputs": ["case_file", "findings", "handoff"],
  "created_at": "..."
}
```

## Project Profile

Defines a project Craik can reason about.

```json
{
  "schema": "craik.project_profile",
  "version": "0.1.0",
  "id": "project_...",
  "name": "stigmem",
  "repo": {
    "type": "git",
    "local_path": "/path/to/repo",
    "remote": "git@github.com:Eidetic-Labs/stigmem.git",
    "default_branch": "main"
  },
  "docs": {
    "paths": ["README.md", "docs/"],
    "immutable_paths": ["docs/adr/"]
  },
  "memory": {
    "backend": "stigmem|local|ephemeral",
    "scope": "team"
  },
  "policies": ["policy_no_adr_edits"]
}
```

## Policy Envelope

Defines what the runtime is allowed and obligated to do.

```json
{
  "schema": "craik.policy_envelope",
  "version": "0.1.0",
  "id": "policy_...",
  "task_id": "task_...",
  "actor": "agent:...",
  "profile": "strict|trusted-local|automation|custom",
  "fail_open": false,
  "allowed_capabilities": ["repo.read", "repo.write.docs", "shell.test", "memory.propose"],
  "denied_capabilities": ["repo.write.adr", "git.force_push"],
  "approval_required": ["github.create_pr", "memory.write.policy"],
  "verification_required": ["git.diff_check"],
  "handoff_required": true,
  "receipt_required": true
}
```

## Capability Grant

Represents a concrete permission for an action family.

```json
{
  "schema": "craik.capability_grant",
  "version": "0.1.0",
  "id": "grant_...",
  "task_id": "task_...",
  "capability": "repo.write.docs",
  "target": {
    "repo": "Eidetic-Labs/stigmem",
    "paths": ["docs/**", "README.md"],
    "exclude": ["docs/adr/**"]
  },
  "operations": ["read", "write", "patch"],
  "expires_at": "...",
  "reason": "Documentation reconciliation task.",
  "approved_by": "user:..."
}
```

## Capability Receipt

Records important actions.

```json
{
  "schema": "craik.capability_receipt",
  "version": "0.1.0",
  "id": "receipt_...",
  "task_id": "task_...",
  "actor": "agent:...",
  "capability": "shell.test",
  "target": "uv run pytest node/tests/plugins",
  "policy_profile": "strict",
  "fail_open": false,
  "reason": "Validate plugin registry docs against test suite.",
  "result": {
    "status": "passed",
    "summary": "43 passed, 12 skipped"
  },
  "created_at": "..."
}
```

## Case File

The case file is assembled before execution.

```json
{
  "schema": "craik.case_file",
  "version": "0.1.0",
  "id": "case_...",
  "task_id": "task_...",
  "objective": "...",
  "policy_envelope_id": "policy_...",
  "facts": [],
  "docs": [],
  "adrs": [],
  "repo_state": {},
  "github_state": {},
  "recent_handoffs": [],
  "stale_risks": [],
  "contradictions": [],
  "verification_plan": []
}
```

## Agent Role Manifest

Defines what an agent role is for.

```json
{
  "schema": "craik.agent_role",
  "version": "0.1.0",
  "id": "role_docs_reviewer",
  "name": "Docs Reviewer",
  "purpose": "Review docs against implementation state.",
  "allowed_modes": ["review"],
  "required_context": ["case_file", "policy_envelope"],
  "default_capabilities": ["repo.read", "memory.read"],
  "output_contract": "craik.worker_result"
}
```

## Worker Result

Specialists return typed results.

```json
{
  "schema": "craik.worker_result",
  "version": "0.1.0",
  "id": "result_...",
  "task_id": "task_...",
  "worker_role": "Docs Reviewer",
  "status": "completed|blocked|failed",
  "findings": [],
  "artifacts": [],
  "proposed_facts": [],
  "open_questions": [],
  "receipts": []
}
```

## Handoff

The durable run summary.

```json
{
  "schema": "craik.handoff",
  "version": "0.1.0",
  "id": "handoff_...",
  "task_id": "task_...",
  "project_id": "project_...",
  "agent": "agent:...",
  "summary": "...",
  "completed_actions": [],
  "files_changed": [],
  "artifacts": [],
  "commands_run": [],
  "tests_run": [],
  "facts_learned": [],
  "facts_invalidated": [],
  "contradictions_opened": [],
  "risks": [],
  "next_steps": [],
  "receipt_ids": [],
  "created_at": "..."
}
```

## Memory Proposal

Agents propose memory updates through a reviewable structure.

```json
{
  "schema": "craik.memory_proposal",
  "version": "0.1.0",
  "id": "memprop_...",
  "task_id": "task_...",
  "operation": "add|update|invalidate",
  "fact": {
    "entity": "repo:...",
    "relation": "codex:current_state",
    "value": "...",
    "source": "agent:...",
    "confidence": 0.95,
    "scope": "team",
    "trust_class": "observed|reported|inferred|policy|external|stale-risk"
  },
  "evidence": [],
  "requires_approval": false
}
```

## Memory Backend Capabilities

Craik should persist detected backend capabilities.

```json
{
  "schema": "craik.memory_backend_capabilities",
  "version": "0.1.0",
  "backend": "stigmem",
  "node_url": "http://127.0.0.1:18765",
  "node_id": "stigmem:node:...",
  "auth_required": true,
  "required": {
    "health": true,
    "metadata": true,
    "fact_write": true,
    "fact_query": true,
    "fact_get": true,
    "fact_provenance": true
  },
  "optional": {
    "recall": true,
    "conflicts": true,
    "source_attestation": "warn|enforce|off",
    "federation": false
  },
  "checked_at": "..."
}
```

## Contradiction Report

Captures incompatible assertions.

```json
{
  "schema": "craik.contradiction_report",
  "version": "0.1.0",
  "id": "contradiction_...",
  "facts": ["fact_a", "fact_b"],
  "summary": "Docs say feature is planned; implementation shows it is merged.",
  "affected_artifacts": [],
  "proposed_resolution": "...",
  "status": "open|resolved|ignored",
  "owner": "user:..."
}
```

## Work Graph Event

Events update the graph.

```json
{
  "schema": "craik.work_graph_event",
  "version": "0.1.0",
  "id": "event_...",
  "task_id": "task_...",
  "type": "created|depends_on|verified_by|contradicts|supersedes|implements|blocks",
  "from": "node_id",
  "to": "node_id",
  "metadata": {},
  "created_at": "..."
}
```
