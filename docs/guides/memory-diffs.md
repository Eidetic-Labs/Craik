# Memory Diffs

<p className="craik-meta"><span>4 min read</span><span>For memory operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- What a memory diff captures across a task.
- The shape of `craik.memory_diff` and how it ties to handoffs.
- How to use diffs in review and audit.

</div>

<div className="craik-keypoint">

**Memory diff**

A structured summary of *what changed in memory* during a single task —
proposals created, proposals approved or rejected, facts written, write
failures, and facts read into the task's working context.

</div>

## Why diffs?

A task's effect on memory is rarely "one fact got written." A typical run
proposes several facts, some of which get approved, some of which get
rejected, some of which collide with existing facts. The diff is the
durable record of all of that — what was attempted, what landed, what was
read along the way.

This matters because:

- **Reviewers** need a single object to inspect when deciding whether a
  run's memory effect was acceptable.
- **Handoffs** carry diff references so the next agent can see what
  memory looked like at the run's boundary.
- **Audit** depends on being able to ask: *"What did this task change?"*
  without piecing it together from raw fact tables.

## Print a diff

```bash title="Show the memory diff for one task"
craik memory diff task_review_docs
```

The diff records:

<div className="craik-grid">

<div>
<h4>Proposals created</h4>
<p>Facts the task proposed during execution, with evidence references and intended scope.</p>
</div>

<div>
<h4>Proposals approved</h4>
<p>Proposals a reviewer accepted, with reviewer identity and approval timestamp.</p>
</div>

<div>
<h4>Proposals rejected</h4>
<p>Proposals declined, with reason and reviewer identity.</p>
</div>

<div>
<h4>Facts written</h4>
<p>Direct writes — distinct from proposals that got promoted. Requires <code>memory.write</code> grant.</p>
</div>

<div>
<h4>Write failures</h4>
<p>Writes the runtime attempted that did not land — scope violation, backend error, redaction failure.</p>
</div>

<div>
<h4>Facts read</h4>
<p>Facts pulled into the task's case-file context. The "what the task was reasoning over" side of the diff.</p>
</div>

</div>

## Today's coverage

The v0.1.x implementation derives **proposal activity** from local state.
This means proposals created, approved, and rejected during the task are
fully recorded.

Direct writes, write failures, and fact reads currently come from local
state only. As runner integrations and the Stigmem write path mature,
those edges attach to the same `craik.memory_diff` contract — the shape
won't change, just the completeness.

:::note
If you're auditing today, treat the proposal sections as authoritative
and the read/write sections as "best-effort, growing." The diff's shape
won't change as coverage expands; new entries will simply start appearing.
:::

## Where diffs live

Diffs persist in the local store under `$CRAIK_HOME/state/`. They're
addressable by task id and joinable into handoffs and receipts:

- Handoffs reference diffs in their `memory_proposals` and `context_debt`
  sections.
- Receipts for `memory.write` and `memory.propose` capabilities reference
  the same diff in their result metadata.
- The work graph projects diffs as `memory_proposal` and `fact` nodes
  connected to the task that produced them.

## Read a diff in review

A practical review pass looks like:

<ol className="craik-steps">
<li>

**Inspect the diff.** `craik memory diff <task-id>` to see the whole story.

</li>
<li>

**Spot-check proposals against evidence.** Each proposal should cite
evidence references. Anything that looks unsupported is a candidate for
rejection.

</li>
<li>

**Look for write failures.** A run that tried to write outside the
approved scope is a stronger signal than the proposals that *did* land.

</li>
<li>

**Confirm scope visibility.** Memory writes are scoped. Make sure the
scope the run wrote into matches the scope the reviewer authorized.

</li>
</ol>

## What's next

<div className="craik-next">

<a href="../memory-proposals/">
<strong>Do</strong>
<span>Manage memory proposals</span>
<small>How proposals flow from a run to reviewer approval.</small>
</a>

<a href="../memory-impact-preview/">
<strong>Do</strong>
<span>Preview impact before promotion</span>
<small>See what a proposal would do to memory before approving it.</small>
</a>

<a href="../../concepts/memory-and-stigmem/">
<strong>Read</strong>
<span>Memory &amp; Stigmem</span>
<small>The memory model Craik composes against.</small>
</a>

</div>
