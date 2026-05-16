# Worker Results

`craik.worker_result` preserves role-specific specialist outputs for
multi-agent coordination. It links a worker's result to the task, optional run,
role, runner metadata, receipts, evidence, handoff, and contradictions.

Worker result status is one of `completed`, `blocked`, `failed`, or `partial`.

Worker results can contain:

- structured findings with severity, evidence, artifact refs, and contradiction ids,
- artifacts,
- assumptions,
- risks,
- proposed actions,
- top-level contradiction ids,
- evidence references,
- receipt ids,
- diagnostics,
- and redaction state.

Specialist outputs should remain typed even when agents disagree. Do not flatten
conflicting results into a single consensus; preserve contradictions and let
review/adjudication decide later.

## Read-Only Investigations

`ReadOnlyInvestigationOrchestrator` creates bounded investigation requests for
specialist roles and persists each returned `craik.worker_result`. The helper
requires a case file, links requests to the active policy envelope, writes
read-only investigation receipts, and blocks work when policy does not allow
`repo.read` or `memory.read`.

Fixture investigations use `FixtureInvestigationSpecialist` for deterministic
local tests. Live specialists should follow the same boundary: read context,
return typed findings, and avoid side effects.
