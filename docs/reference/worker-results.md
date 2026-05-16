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
