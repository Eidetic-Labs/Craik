# Self-audit

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `self_audit` object every structured handoff includes — what each
field means and how incomplete runs still produce auditable handoffs.

</div>

<div className="craik-keypoint">

**Blocked runs still produce handoffs.**

A blocked or incomplete handoff may have
<code>validation_recorded = false</code>, but it must explain the gap
in <code>risks</code>, <code>context_debt</code>, or
<code>next_steps</code>.

</div>

## Fields

| Field | Meaning |
| --- | --- |
| `schema_validated` | The handoff was validated against the `craik.handoff` schema. |
| `redaction_reviewed` | The handoff passed through redaction-aware persistence boundaries. |
| `receipts_reviewed` | The writer checked task receipts and attached receipt ids when available. |
| `assumptions_reviewed` | The writer reviewed case-file assumptions or marked that no case file was available. |
| `validation_recorded` | The handoff records validation in `tests_run`. |
| `policy_exceptions_disclosed` | Policy exceptions and fail-open notes were explicitly recorded, even when none were used. |
| `notes` | Additional self-audit notes. |

## What's next

<div className="craik-next">

<a href="../../guides/writing-handoffs/">
<strong>Guide</strong>
<span>Writing handoffs</span>
<small>The writer-facing workflow this audit constrains.</small>
</a>

<a href="../exit-discipline/">
<strong>Reference</strong>
<span>Exit discipline</span>
<small>The exit-discipline checklist that builds on self-audit.</small>
</a>

<a href="../handoff-viewer/">
<strong>Reference</strong>
<span>Handoff viewer</span>
<small>How the audit fields surface in the operator view.</small>
</a>

</div>
