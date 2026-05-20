# Training trajectory exports

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The stable review-and-replay format for self-improvement loops —
`TrainingTrajectoryExport`, the per-step decision record, redaction
posture, compatibility rules, and the compressed summary form.

</div>

<div className="craik-keypoint">

**Review and replay, not raw trace.**

Exports are designed for review and replay fixtures. They are not a
raw trace dump and must not be used to reconstruct private prompts or
local workspace state.

</div>

## Export record

`TrainingTrajectoryExport`:

<div className="craik-grid">

<div><h4><code>schema: craik.training_trajectory_export</code></h4></div>
<div><h4><code>format_version: craik.training_trajectory.v1</code></h4></div>
<div><h4>Task id and outcome</h4></div>
<div><h4>Ordered decisions</h4><p>From runner step results.</p></div>
<div><h4>Receipt references and redacted payloads</h4></div>
<div><h4>Evidence references and redacted payloads</h4></div>
<div><h4>Compatibility notes</h4></div>
<div><h4>Redaction paths</h4></div>

</div>

## Per-step decision

`TrainingTrajectoryDecision`:

<div className="craik-grid">

<div><h4>Step result id</h4></div>
<div><h4>Phase</h4></div>
<div><h4>Runner id</h4></div>
<div><h4>Status</h4></div>
<div><h4>Summary</h4></div>
<div><h4>Observed output</h4></div>
<div><h4>Diagnostics</h4></div>
<div><h4>Artifacts</h4></div>
<div><h4>Receipt ids</h4></div>
<div><h4>Evidence ids</h4></div>

</div>

## Redaction boundary

<div className="craik-keypoint">

**Ids and summaries, never raw payloads.**

Trajectory exports redact secret-like values, private payload fields,
prompts, responses, traces, raw outputs, raw trajectories, credentials,
and local-only filesystem paths. Local filesystem paths are replaced
with <code>[LOCAL_PATH]</code>; secret-like values use the shared
redaction marker.

</div>

## Compatibility

<div className="craik-keypoint">

**Forward-compatible by default.**

Consumers use <code>format_version</code> to select parsing behavior.
Producers may add fields to the export envelope or decision records;
consumers should ignore unknown fields and preserve the original
<code>format_version</code> when forwarding an export.

</div>

## Compression

`TrainingTrajectorySummary` compresses an export into a reviewable
summary.

<div className="craik-grid">

<div><h4>Source export id</h4></div>
<div><h4>Task id and outcome</h4></div>
<div><h4>Decision count</h4></div>
<div><h4>Phase and status counts</h4></div>
<div><h4>Selected redacted summary lines</h4></div>
<div><h4>Omitted decision ids</h4></div>
<div><h4>Receipt · evidence · policy envelope ids</h4></div>
<div><h4>Replay fixture &amp; result ids</h4></div>
<div><h4>Unresolved risk ids</h4></div>

</div>

<div className="craik-keypoint">

**Compression must not remove required replay context.**

Replay fixture and result ids remain top-level fields even when the
decision that introduced them is omitted from the summary lines.
Consumers that need full diagnostics, artifacts, observed output, or
per-step timestamps must load the source export.

</div>

## What's next

<div className="craik-next">

<a href="../skill-replay/">
<strong>Reference</strong>
<span>Skill replay</span>
<small>The replay-fixture contract trajectories support.</small>
</a>

<a href="../learning-receipts/">
<strong>Reference</strong>
<span>Learning receipts</span>
<small>Record export decisions with the <code>export</code> action.</small>
</a>

<a href="../../guides/learning-loops/">
<strong>Guide</strong>
<span>Learning loops</span>
<small>The discipline trajectories support.</small>
</a>

</div>
