# Structured debates

<p className="craik-meta"><span>3 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

How bounded multi-agent disagreement is captured without erasing
minority positions — the `debate_turn` and `debate_summary` contracts,
their boundaries, and how renderers stay deterministic.

</div>

<div className="craik-keypoint">

**Coordination records, not consensus.**

Debates preserve the basis for each position. They do not silently
choose a winner.

</div>

## Contracts

<div className="craik-fields">

<div>
<dt>Contract</dt>
<dt><span className="craik-fields__type">Records</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>craik.debate_turn</code></dt>
<dt><span className="craik-fields__type">contribution</span></dt>
<dd><code>role_id</code> &amp; <code>role_kind</code> · <code>worker_result_id</code> link · <code>position</code> (supports / opposes / clarifies / questions / blocks) · <code>evidence_ids</code> · <code>assumption_ids</code> · <code>contradiction_ids</code>.</dd>
</div>

<div>
<dt><code>craik.debate_summary</code></dt>
<dt><span className="craik-fields__type">outcome</span></dt>
<dd>Deterministic outcome record — see outcomes below.</dd>
</div>

</div>

## Debate outcomes

<div className="craik-fields">

<div>
<dt>Outcome</dt>
<dt><span className="craik-fields__type">Use when</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>agreement</code></dt>
<dt><span className="craik-fields__type">consensus</span></dt>
<dd>Support turns reached the same bounded conclusion and no opposing or blocking turn remains.</dd>
</div>

<div>
<dt><code>unresolved_disagreement</code></dt>
<dt><span className="craik-fields__type">human review</span></dt>
<dd>Preserves a conflict without opening a contradiction report. Use when the orchestrator needs human or adjudicator review but the disagreement is not yet known to be an incompatible factual assertion.</dd>
</div>

<div>
<dt><code>contradiction_opened</code></dt>
<dt><span className="craik-fields__type">incompatible facts</span></dt>
<dd>Links to one or more <code>craik.contradiction_report</code> records when specialist outputs assert incompatible facts or mutually exclusive implementation status.</dd>
</div>

</div>

## Boundaries

<div className="craik-keypoint">

**Scoped to task and topic.**

A turn can cite evidence or assumptions, but it must not promote
assumptions to facts. A summary can list next steps, but it must not
silently choose a winner when a blocker or opposing specialist output
remains unresolved.

</div>

## Rendering

Markdown and JSON rendering are deterministic. Renderers keep turn
order from `turn_ids`, sort evidence-style lists where order has no
semantic meaning, and emit explicit `None` rows for empty sections so
absent agreement or contradiction links are visible in review.

## What's next

<div className="craik-next">

<a href="../cross-agent-review/">
<strong>Reference</strong>
<span>Cross-agent review</span>
<small>The review flow debates feed.</small>
</a>

<a href="../agent-roles/">
<strong>Reference</strong>
<span>Agent roles</span>
<small>The role kinds that produce turns.</small>
</a>

<a href="../schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The <code>debate_turn</code> / <code>debate_summary</code> shapes.</small>
</a>

</div>
