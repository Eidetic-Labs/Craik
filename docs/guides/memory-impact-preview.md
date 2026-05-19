# Memory Impact Preview

<p className="craik-meta"><span>4 min read</span><span>For reviewers</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- What a memory impact preview shows you *before* promotion.
- The signals reviewers should look at: contradictions, evidence, scope.
- When a preview is enough, and when you should ask for a direct
  `memory.write` grant.

</div>

<div className="craik-keypoint">

**Memory impact preview**

A read-only forecast of what would happen if you promoted the pending
proposals for a task — facts that would be added, facts that would be
invalidated, contradictions that would surface, and the scope visibility
of every change.

Previews never write. They surface enough information to make a decision.

</div>

## Run a preview

```bash title="Show the impact of promoting task_review_docs"
craik memory preview task_review_docs
```

The preview prints:

<div className="craik-grid">

<div>
<h4>Facts that would be added</h4>
<p>The net-new facts a promotion would create, with the scope each one lands in.</p>
</div>

<div>
<h4>Facts that would be invalidated</h4>
<p>Existing facts a promotion would supersede or retire.</p>
</div>

<div>
<h4>Likely contradictions</h4>
<p>Proposals that conflict with existing approved facts, surfaced for explicit resolution.</p>
</div>

<div>
<h4>Proposals missing evidence</h4>
<p>Pending proposals without sufficient evidence references — almost always a "no" until evidence is attached.</p>
</div>

<div>
<h4>Scope visibility counts</h4>
<p>How many actors / projects each scope reaches. The "blast radius" view.</p>
</div>

</div>

## What to look at first

When a preview lands on your desk, the priority order is roughly:

<ol className="craik-steps">
<li>

**Proposals missing evidence.** If a proposal claims a fact without
citing a file, issue, or upstream memory record, reject it or ask for the
evidence to be attached. Evidence-free facts contaminate memory faster
than anything else.

</li>
<li>

**Likely contradictions.** A contradiction is the runtime telling you
*"this proposal disagrees with something already trusted."* Decide which
side wins before you approve, and use the contradiction inbox to record
the decision.

</li>
<li>

**Scope visibility.** A proposal that wants to land in a wide scope
(`project:*`, `org:*`) deserves more skepticism than one scoped to a
single project.

</li>
<li>

**Invalidations.** Confirm that retiring an existing fact is the actual
intent. Sometimes a "would invalidate" surfaces because the new proposal
should have been narrower, not because the old fact is wrong.

</li>
</ol>

## Previews are explicit about scope

Memory scope is intentionally first-class in the preview output. Reviewers
should confirm three things before approving:

<div className="craik-fields">

<div>
<dt>Question</dt>
<dt><span className="craik-fields__type">Signal</span></dt>
<dd>Where it lives</dd>
</div>

<div>
<dt>Is the scope appropriate?</dt>
<dt><span className="craik-fields__type">visibility</span></dt>
<dd>Each pending proposal carries its target scope. Anything wider than the run was authorized for is a red flag.</dd>
</div>

<div>
<dt>Is there evidence?</dt>
<dt><span className="craik-fields__type">supported_by</span></dt>
<dd>Every proposal should cite at least one evidence reference. "No evidence" is a default-reject signal.</dd>
</div>

<div>
<dt>Are there contradictions?</dt>
<dt><span className="craik-fields__type">contradictions</span></dt>
<dd>Resolve before promotion. The contradiction inbox is the durable record of how you resolved it.</dd>
</div>

</div>

## Previews don't grant authority

A preview is a read-only forecast. Promotion of proposals still requires
the reviewer flow. **Direct writes to Stigmem or a memory backend still
require a matching `memory.write` grant** — when that grant is absent,
agents must leave proposals for review instead of writing directly.

If you find yourself wanting to bypass the proposal flow because "the
review step is tedious," that's usually a signal that:

- The policy envelope doesn't yet match the task's risk profile (consider
  adding a `memory.write` grant scoped narrowly to the affected memory
  scope), **or**
- The proposals are too granular (consider batching proposals at the
  handoff boundary so review is a single pass).

## What's next

<div className="craik-next">

<a href="memory-proposals.md">
<strong>Do</strong>
<span>Manage memory proposals</span>
<small>The full proposal lifecycle from creation to approval.</small>
</a>

<a href="contradiction-inbox.md">
<strong>Do</strong>
<span>Resolve contradictions</span>
<small>How conflicting facts are surfaced, recorded, and resolved.</small>
</a>

<a href="../concepts/memory-and-stigmem.md">
<strong>Read</strong>
<span>Memory &amp; Stigmem</span>
<small>Why memory is governed and how scope, evidence, and trust compose.</small>
</a>

</div>
