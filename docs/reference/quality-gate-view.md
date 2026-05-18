# Quality Gate View

The quality gate view is a read-only operator display for handoff quality
scores, evidence coverage scores, runtime critic findings, and red-team
findings.

The v0.7.0 TUI surface formats:

- handoff score bands and blocking reasons;
- evidence coverage score bands, missing evidence, and weak claims;
- critic findings by review status and severity;
- red-team findings, including blocking state;
- adjudication links when a finding has been reviewed.

## Gate States

The view reports a display-only gate state:

- `blocked` when a handoff or evidence score is poor, or an unadjudicated
  red-team finding is blocking;
- `reviewable` when high or critical critic findings remain reviewable, or any
  score is adequate rather than excellent;
- `clear` when no scores or findings require operator attention.

This state does not mutate policy or approve work. It is a compact operator
summary of the underlying contracts.

## Authority Boundary

Runtime critic and red-team findings remain non-authoritative unless a separate
adjudication accepts, revises, rejects, or defers them. The view shows
`authoritative=false` and any adjudication ID so operators can distinguish
review signals from accepted decisions.

See [Quality Scores](quality-scores.md) and
[Runtime Critics And Red Team](runtime-critics.md) for the underlying contract
behavior.
