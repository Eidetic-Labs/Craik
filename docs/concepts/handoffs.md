# Handoffs

<p className="craik-meta"><span>5 min read</span><span>Core concept</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- What a handoff is and what it's deliberately *not*.
- The fields every handoff carries and how they ground the next run.
- How structured handoffs and Markdown rendering coexist.
- What the self-audit checklist tells you about a finished run.

</div>

<div className="craik-keypoint">

**Handoff**

A durable, structured run summary for the next agent or human reviewer.
It records what happened, what was validated, what remains uncertain, and
where to resume.

A handoff is **not** a transcript and **not** a chat log. It's the concise
continuity record that lets the next actor pick up without re-deriving
everything from scratch.

</div>

## The contract

Every handoff carries:

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt>task_id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>The task this handoff closes (or pauses).</dd>
</div>

<div>
<dt>project_id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>The project the task belongs to.</dd>
</div>

<div>
<dt>intent_lock_id</dt>
<dt><span className="craik-fields__type">id</span></dt>
<dd>The scope contract the run executed under.</dd>
</div>

<div>
<dt>agent</dt>
<dt><span className="craik-fields__type">agent_identity</span></dt>
<dd>Which runner produced the handoff — Codex, Claude, Gemini, a human, etc.</dd>
</div>

<div>
<dt>status</dt>
<dt><span className="craik-fields__type">enum</span></dt>
<dd><code>completed</code> · <code>paused</code> · <code>failed</code> · <code>requires_review</code>.</dd>
</div>

<div>
<dt>summary</dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>One paragraph: what was attempted, what landed, what the next actor needs to know first.</dd>
</div>

<div>
<dt>completed_actions</dt>
<dt><span className="craik-fields__type">action[]</span></dt>
<dd>The discrete units of work that did finish.</dd>
</div>

<div>
<dt>files_and_artifacts</dt>
<dt><span className="craik-fields__type">artifact_ref[]</span></dt>
<dd>Paths the run touched and named artifacts it produced.</dd>
</div>

<div>
<dt>commands_and_validation</dt>
<dt><span className="craik-fields__type">command[]</span></dt>
<dd>Validation commands run and their results — the verification trail.</dd>
</div>

<div>
<dt>assumptions</dt>
<dt><span className="craik-fields__type">assumption[]</span></dt>
<dd>Open assumptions promoted, refuted, or carried forward from the case file.</dd>
</div>

<div>
<dt>context_debt</dt>
<dt><span className="craik-fields__type">debt_item[]</span></dt>
<dd>Context this run knows it didn't fully chase. Material for the next run.</dd>
</div>

<div>
<dt>policy_exceptions</dt>
<dt><span className="craik-fields__type">exception[]</span></dt>
<dd>Cases where the run took a fail-open path or hit a policy boundary.</dd>
</div>

<div>
<dt>receipts</dt>
<dt><span className="craik-fields__type">id[]</span></dt>
<dd>Receipt ids produced during the run. Joinable to <code>capability_receipt</code> records.</dd>
</div>

<div>
<dt>memory_proposals</dt>
<dt><span className="craik-fields__type">proposal[]</span></dt>
<dd>Facts the run wants written to memory, pending review.</dd>
</div>

<div>
<dt>next_steps</dt>
<dt><span className="craik-fields__type">step[]</span></dt>
<dd>Explicit next actions: what should happen, who should do it, what to verify first.</dd>
</div>

<div>
<dt>self_audit</dt>
<dt><span className="craik-fields__type">checklist</span></dt>
<dd>The honesty pass — see below.</dd>
</div>

</div>

## Structured *and* Markdown

Craik persists handoffs as `craik.handoff` records in the local SQLite store.
The structured handoff is the durable source of truth. The Markdown
rendering is a readable view of the same record — useful for code review,
release notes, and "tell me what just happened" inspection.

```bash title="Create a structured handoff"
craik handoff create task_review_docs \
  --summary "Updated docs and recorded current state." \
  --test-run pytest
```

```bash title="Render the same handoff as Markdown"
craik handoff show task_review_docs --markdown
```

```bash title="Export the structured JSON"
craik handoff show task_review_docs
```

## The self-audit

Every handoff includes a self-audit checklist that asks explicit questions
about the run:

<div className="craik-grid">

<div>
<h4><code>schema_validated</code></h4>
<p>Did the runtime check that produced records match their declared schemas?</p>
</div>

<div>
<h4><code>redaction_reviewed</code></h4>
<p>Did someone (human or runtime) confirm receipts and handoffs are free of unredacted secrets?</p>
</div>

<div>
<h4><code>receipts_reviewed</code></h4>
<p>Were the produced receipts inspected and joined back to the actions they describe?</p>
</div>

<div>
<h4><code>assumptions_reviewed</code></h4>
<p>Were open assumptions promoted, refuted, or explicitly carried forward?</p>
</div>

<div>
<h4><code>validation_recorded</code></h4>
<p>Are the commands run and their outcomes captured in <code>commands_and_validation</code>?</p>
</div>

<div>
<h4><code>policy_exceptions_disclosed</code></h4>
<p>Are all fail-open paths and policy boundary hits called out in <code>policy_exceptions</code>?</p>
</div>

</div>

**Incomplete handoffs are valid** — a run that crashed mid-stream still
writes one. What's not valid is hiding that incompleteness. The self-audit
makes missing validation or unresolved context visible to whoever picks up
the work next.

## How the next agent uses a handoff

When `craik onboard` runs for the next task, it pulls in the most recent
handoffs for the project (`recent_handoffs` in the onboarding payload).
The next agent's case file inherits:

- The `summary` so context isn't reconstructed from scratch.
- Open `assumptions` and `context_debt` as carryovers.
- `policy_exceptions` so the new runner knows where the system was running
  hot.
- `next_steps` as a starting menu of actions.

That is the loop. Each handoff is a node in the work graph. Receipts are
the edges that explain how the run got from case file to handoff.

## What's next

<div className="craik-next">

<a href="work-graph.md">
<strong>Read next</strong>
<span>The work graph</span>
<small>How tasks, case files, receipts, and handoffs compose into the queryable runtime state.</small>
</a>

<a href="../guides/writing-handoffs.md">
<strong>Do</strong>
<span>Write good handoffs</span>
<small>Patterns that make a handoff actually useful for the next agent.</small>
</a>

<a href="../reference/handoff-viewer.md">
<strong>Reference</strong>
<span>Handoff viewer</span>
<small>The operator surface that renders a handoff with full context.</small>
</a>

</div>
