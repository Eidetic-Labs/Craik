# Recovery mode

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The bounded continuity view a resuming agent receives — the latest
handoff, available case files, receipts, open contradictions, and
active instruction constraints for a project or task.

</div>

<div className="craik-keypoint">

**Continuity aid, not policy.**

Recovery mode does not resolve contradictions, promote facts, or
replace policy checks. A non-clean recovery session tells the agent
what must be reviewed before continuing.

</div>

## Contracts

<div className="craik-fields">

<div>
<dt>Contract</dt>
<dt><span className="craik-fields__type">Records</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>craik.run_delta</code></dt>
<dt><span className="craik-fields__type">delta</span></dt>
<dd>Previous and current handoff ids · case file ids · receipt ids · open contradiction ids · active promoted instruction constraint ids · stable list of change items.</dd>
</div>

<div>
<dt><code>craik.recovery_session</code></dt>
<dt><span className="craik-fields__type">resume state</span></dt>
<dd>Links to a run delta and classifies the resume state.</dd>
</div>

</div>

## Resume statuses

| Status | Meaning |
| --- | --- |
| `clean_resume` | A latest handoff exists and no blocking changed state was found. |
| `changed_state` | A handoff exists, but open contradictions or active instruction constraints require review. |
| `missing_prior_context` | No prior handoff is available for the requested scope. |

<div className="craik-keypoint">

**Non-clean sessions name the work.**

Non-clean recovery sessions must include <code>required_actions</code>
so an agent does not silently continue through missing or changed
context.

</div>

## Boundaries

Recovery summaries are derived from already-persisted local store
records. They do not query remote GitHub state, inspect the working
tree, or fetch Stigmem facts by themselves. Callers should refresh
those inputs separately, persist the resulting receipts or
contradictions, and then rebuild recovery mode.

## What's next

<div className="craik-next">

<a href="run-delta-view/">
<strong>Reference</strong>
<span>Run delta view</span>
<small>The operator-facing delta surface.</small>
</a>

<a href="exit-discipline/">
<strong>Reference</strong>
<span>Exit discipline</span>
<small>How handoffs and recovery interact.</small>
</a>

<a href="schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The <code>run_delta</code> / <code>recovery_session</code> shapes.</small>
</a>

</div>
