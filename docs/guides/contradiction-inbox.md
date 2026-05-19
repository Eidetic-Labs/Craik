# Contradiction Inbox

<p className="craik-meta"><span>5 min read</span><span>For reviewers</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Open, inspect, and triage local contradiction reports — the workflow-level
conflicts that don't necessarily map to Stigmem memory conflicts. By the
end you'll know how to file a report, the fields every report carries,
and how local reports relate to Stigmem-level conflicts.

</div>

<div className="craik-keypoint">

**Local contradiction report**

A first-class workflow record for "two things disagree" — docs vs.
implementation, handoff vs. branch state, reviewer vs. implementer,
public docs vs. internal-only content. Not the same as a Stigmem memory
conflict, though it can reference one.

</div>

## Open a report

```bash title="File a contradiction"
craik contradictions open \
  --task-id task_review_docs \
  --summary "Docs conflict with implementation." \
  --fact fact_docs_planned \
  --fact fact_cli_implemented \
  --affected-artifact README.md \
  --evidence-id evidence_readme_status \
  --owner user:maintainer
```

## List and inspect

```bash title="Open queue"
craik contradictions list --status open
```

```bash title="One report and its linked evidence"
craik contradictions show \
  contradiction_task_review_docs_docs_conflict_with_implementation
```

## What a report carries

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt>conflicting_facts</dt>
<dt><span className="craik-fields__type">fact_id[] · text[]</span></dt>
<dd>The fact ids or plain-language statements in conflict.</dd>
</div>

<div>
<dt>affected_artifacts</dt>
<dt><span className="craik-fields__type">artifact_ref[]</span></dt>
<dd>Files, docs, or PRs the contradiction touches.</dd>
</div>

<div>
<dt>evidence_ids</dt>
<dt><span className="craik-fields__type">evidence_id[]</span></dt>
<dd>Evidence references that show the conflict directly.</dd>
</div>

<div>
<dt>owner</dt>
<dt><span className="craik-fields__type">operator_uri</span></dt>
<dd>Who is responsible for resolving this report.</dd>
</div>

<div>
<dt>proposed_resolution</dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>The reporter's suggested resolution. Reviewers can override.</dd>
</div>

<div>
<dt>status</dt>
<dt><span className="craik-fields__type">enum</span></dt>
<dd><code>open</code> · <code>resolved</code> · <code>dismissed</code> · <code>linked_to_stigmem</code>.</dd>
</div>

<div>
<dt>stigmem_conflict_id</dt>
<dt><span className="craik-fields__type">id (optional)</span></dt>
<dd>The matching Stigmem memory conflict, when one exists.</dd>
</div>

</div>

Reports are **local workflow items**. They're redacted before storage and
appear in work-graph exports when linked to a task.

## Local reports vs Stigmem conflicts

<div className="craik-decision">

<div>
<h4>Local contradiction report</h4>
<ul>
<li>Workflow-level conflict between artifacts or runtime decisions.</li>
<li>Examples: docs disagree with implementation; a handoff disagrees with branch state; a reviewer result disagrees with an implementer result; public docs contain content that should be internal.</li>
<li>Resolved by editing artifacts, updating intent locks, or filing a new task.</li>
<li>Lives in Craik local state.</li>
</ul>
</div>

<div>
<h4>Stigmem memory conflict</h4>
<ul>
<li>Memory-substrate conflict between facts in Stigmem.</li>
<li>Tracked by Stigmem itself, with its own contradiction-handling primitives.</li>
<li>Resolved through Stigmem's federation / approval flow.</li>
<li>Requires explicit memory-write authority to resolve from inside Craik.</li>
</ul>
</div>

</div>

When a Stigmem conflict matches a local contradiction, store its id in
`stigmem_conflict_id`. The local report becomes the workflow tracking
layer; Stigmem handles the memory-substrate resolution.

## A pragmatic resolution flow

<ol className="craik-steps">
<li>

**Read the evidence.** Confirm both sides of the conflict are
substantiated. If one side has no evidence, the resolution is to drop
that side.

</li>
<li>

**Decide which artifact moves.** Often the conflict is signal that
docs, code, or a fact needs to change — not that both should somehow
coexist.

</li>
<li>

**File the change as a new task.** The contradiction report names the
problem; a follow-up task with its own intent lock and case file does
the work.

</li>
<li>

**Update the report on resolution.** Mark `resolved` (or `dismissed`
with reason). The report stays addressable for audit.

</li>
<li>

**Link to Stigmem if applicable.** When the conflict touches a memory
fact, set `stigmem_conflict_id` so the trail is joinable.

</li>
</ol>

## What's next

<div className="craik-next">

<a href="memory-proposals.md">
<strong>Do</strong>
<span>Memory proposals</span>
<small>Where new facts go when they're proposed against a contradicted memory.</small>
</a>

<a href="../concepts/memory-and-stigmem.md">
<strong>Read</strong>
<span>Memory &amp; Stigmem</span>
<small>The memory model Craik composes against.</small>
</a>

<a href="../reference/contradiction-inbox-view.md">
<strong>Reference</strong>
<span>Contradiction inbox view</span>
<small>The operator surface that renders the inbox with full context.</small>
</a>

</div>
