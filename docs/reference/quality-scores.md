# Quality scores

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The two derived review records that help agents decide whether a
handoff or evidence set is ready to rely on —
`craik.handoff_quality_score` and `craik.evidence_coverage_score`.

</div>

<div className="craik-keypoint">

**Not proof of truth.**

Quality scores help agents decide whether to rely on a handoff or
evidence set. They are not permission to skip policy review.

</div>

## Handoff quality

`craik.handoff_quality_score` summarizes whether a handoff is useful
for continuation.

**Inputs:**

<div className="craik-grid">

<div><h4>Summary &amp; completed actions</h4></div>
<div><h4>Validation records</h4></div>
<div><h4>Linked receipts</h4></div>
<div><h4>Evidence-bearing artifacts</h4><p>Adjudications · receipts.</p></div>
<div><h4>Context debt</h4></div>
<div><h4>Unresolved risks &amp; disagreements</h4></div>
<div><h4>Next steps</h4></div>
<div><h4>Self-audit checklist</h4></div>

</div>

**Score bands** (normalized `0.0` – `1.0`):

| Band | Range |
| --- | --- |
| `excellent` | `0.85` to `1.0` |
| `adequate` | `0.60` to less than `0.85` |
| `poor` | less than `0.60` |

<div className="craik-keypoint">

**Poor scores name the work.**

Poor handoff scores must include <code>blocking_reasons</code> so a
resuming agent knows what to repair.

</div>

## Evidence coverage

`craik.evidence_coverage_score` compares evidence ids present in a
handoff or output with evidence ids required by the caller. Missing
ids and weak claims are preserved explicitly.

<div className="craik-keypoint">

**Coverage ≠ certainty.**

A complete set of links means the expected references are present —
not that the underlying claims are true.

</div>

## What's next

<div className="craik-next">

<a href="runtime-critics/">
<strong>Reference</strong>
<span>Runtime critics &amp; red team</span>
<small>The reviewable findings that compose with scores.</small>
</a>

<a href="self-audit/">
<strong>Reference</strong>
<span>Self-audit</span>
<small>The handoff-side checklist scores read.</small>
</a>

<a href="quality-gate-view/">
<strong>Reference</strong>
<span>Quality gate view</span>
<small>The operator surface that surfaces scores.</small>
</a>

</div>
