# Training Trajectory Exports

Training trajectory exports provide a stable review and replay format for
self-improvement loops.

`TrainingTrajectoryExport` records:

- schema: `craik.training_trajectory_export`;
- format version: `craik.training_trajectory.v1`;
- task id and outcome;
- ordered decisions from runner step results;
- receipt references and redacted receipt payloads;
- evidence references and redacted evidence payloads;
- compatibility notes;
- redaction paths.

`TrainingTrajectoryDecision` records one step in the trajectory:

- step result id;
- phase;
- runner id;
- status;
- summary;
- observed output;
- diagnostics;
- artifacts;
- receipt ids;
- evidence ids.

## Redaction Boundary

Trajectory exports redact secret-like values, private payload fields, prompts,
responses, traces, raw outputs, raw trajectories, credentials, and local-only
filesystem paths. Exported records preserve ids and summaries instead of private
payloads.

Local filesystem paths are replaced with `[LOCAL_PATH]`. Secret-like values use
the shared redaction marker.

## Compatibility

Consumers must use `format_version` to select parsing behavior. Producers may
add fields to the export envelope or decision records; consumers should ignore
unknown fields and preserve the original `format_version` when forwarding an
export.

Exports are designed for review and replay fixtures. They are not a raw trace
dump and should not be used to reconstruct private prompts or local workspace
state.
