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

## Compression

`TrainingTrajectorySummary` compresses a trajectory export into a reviewable
summary. It records:

- source export id;
- task id and outcome;
- decision count;
- phase and status counts;
- selected redacted summary lines;
- omitted decision ids;
- receipt ids;
- evidence ids;
- policy envelope ids;
- replay fixture ids;
- replay result ids;
- unresolved risk ids.

Compressed summaries preserve links needed for replay and review, but they do
not preserve every decision field. Consumers that need full diagnostics,
artifacts, observed output, or per-step timestamps must load the source export.

Compression must not remove required replay context. Replay fixture and result
ids remain top-level fields even when the decision that introduced them is
omitted from the summary lines.
