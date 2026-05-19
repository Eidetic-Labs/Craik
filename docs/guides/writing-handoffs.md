# Writing Handoffs

<p className="craik-meta"><span>5 min read</span><span>For operators &amp; runners</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Write a handoff that lets the next agent — model or human — pick up your
work without re-deriving everything. By the end you'll know the required
shape, the patterns that make handoffs actually useful, and the
self-audit fields you should never skip.

</div>

## Before you write

Make sure the task has a current case file:

```bash title="Refresh the case file if needed"
craik case build task_review_docs
```

The handoff writer derives `assumptions` and `context_debt` from the
latest case file when available. It also derives `receipts` from
persisted receipts for the task — anything you produced during the run
will be referenced automatically.

## 1 · The minimum viable handoff

```bash title="A handoff with the basics"
craik handoff create task_review_docs \
  --summary "Reviewed docs against implementation." \
  --agent agent:codex \
  --completed-action "Compared README and docs against runtime behavior." \
  --test-run pytest \
  --next-step "Review memory backend assumptions."
```

This is a valid handoff — but it's the floor, not the ceiling.

## 2 · Render it back

```bash title="Structured JSON"
craik handoff show task_review_docs
```

```bash title="Markdown rendering for review"
craik handoff show task_review_docs --markdown
```

The structured handoff is the durable source of truth. The Markdown is a
readable rendering of the same record — useful for code review, release
notes, or pasting into a Slack thread.

## 3 · Use status to be honest

When the run didn't complete, declare it:

<div className="craik-fields">

<div>
<dt>Status</dt>
<dt><span className="craik-fields__type">When to use</span></dt>
<dd>What it tells the next agent</dd>
</div>

<div>
<dt><code>completed</code></dt>
<dt><span className="craik-fields__type">default</span></dt>
<dd>Work landed; verification passed. Self-audit fields should reflect this.</dd>
</div>

<div>
<dt><code>incomplete</code></dt>
<dt><span className="craik-fields__type">partial</span></dt>
<dd>Useful progress, but the objective isn't fully met. <code>next_steps</code> should be concrete.</dd>
</div>

<div>
<dt><code>blocked</code></dt>
<dt><span className="craik-fields__type">stop condition hit</span></dt>
<dd>External dependency, missing capability grant, or a contradiction needing review.</dd>
</div>

<div>
<dt><code>failed</code></dt>
<dt><span className="craik-fields__type">work could not proceed</span></dt>
<dd>Runtime error, hard policy denial, or unrecoverable assumption mismatch.</dd>
</div>

</div>

Pass the status explicitly when relevant:

```bash title="A blocked handoff"
craik handoff create task_review_docs \
  --status blocked \
  --summary "Stopped at memory.write — no grant in current envelope." \
  --next-step "Operator must approve a memory.write grant or convert to a memory proposal."
```

## What good handoffs include

<div className="craik-grid">

<div>
<h4>What changed</h4>
<p>Files touched, artifacts produced, side effects performed. Concrete.</p>
</div>

<div>
<h4>What was validated</h4>
<p>Tests run, linters passed, policies confirmed. Use <code>--test-run</code> and <code>--completed-action</code> liberally.</p>
</div>

<div>
<h4>Open assumptions</h4>
<p>Carry forward the assumptions the case file flagged that the run did not resolve.</p>
</div>

<div>
<h4>Receipt references</h4>
<p>The handoff writer auto-attaches receipts produced under the task. Skim them before sealing.</p>
</div>

<div>
<h4>Policy exceptions</h4>
<p>Any fail-open paths, denied capabilities, or boundary hits. Disclosure is the rule.</p>
</div>

<div>
<h4>Context debt</h4>
<p>Sources omitted, deferred, or unavailable. The next run gets to inherit this.</p>
</div>

<div>
<h4>Memory proposals</h4>
<p>Facts the run wants to land. The reviewer's queue.</p>
</div>

<div>
<h4>Concrete next steps</h4>
<p>What should happen, who should do it, what to verify first. The most-read field.</p>
</div>

</div>

## Patterns that hurt the next agent

<div className="craik-decision">

<div>
<h4>Do</h4>
<ul>
<li>Use concrete <code>--completed-action</code> entries: <em>"Updated docs/architecture.md to match runtime"</em>.</li>
<li>Cite receipt ids in the summary when they prove a claim.</li>
<li>Carry forward assumptions verbatim — don't paraphrase.</li>
<li>Write <code>--next-step</code> in the imperative: <em>"Review memory backend assumptions"</em>.</li>
</ul>
</div>

<div>
<h4>Avoid</h4>
<ul>
<li>Vague summaries: <em>"Reviewed and fixed."</em> Fix what? With what evidence?</li>
<li>Promoting assumptions to "fact" in the handoff without an evidence reference.</li>
<li>Hiding fail-open paths by leaving <code>policy_exceptions</code> empty.</li>
<li>Skipping <code>--test-run</code> when validation did happen — silence reads as "didn't run."</li>
</ul>
</div>

</div>

## The self-audit checklist

Every handoff includes a self-audit. The next agent (and the next operator)
read it first. Don't lie to the audit:

<ol className="craik-steps">
<li>

**Schema validated.** The runtime checked records against declared
schemas — leave this true.

</li>
<li>

**Redaction reviewed.** Confirm receipts and handoffs are free of
unredacted secrets. If you didn't review, mark it false.

</li>
<li>

**Receipts reviewed.** Were the produced receipts inspected and joined
back to the actions they describe?

</li>
<li>

**Assumptions reviewed.** Were open assumptions promoted, refuted, or
explicitly carried forward?

</li>
<li>

**Validation recorded.** Are the commands run and outcomes captured in
`commands_and_validation`?

</li>
<li>

**Policy exceptions disclosed.** Are all fail-open paths and boundary
hits called out?

</li>
</ol>

Incomplete handoffs are valid. **Dishonest** handoffs are not — they
contaminate the next run's context.

## What's next

<div className="craik-next">

<a href="../concepts/handoffs.md">
<strong>Read</strong>
<span>Handoff concept</span>
<small>The typed object you just produced and how it composes with the work graph.</small>
</a>

<a href="memory-proposals.md">
<strong>Do</strong>
<span>Memory proposals</span>
<small>What to do with the proposals your handoff emitted.</small>
</a>

<a href="../reference/handoff-viewer.md">
<strong>Reference</strong>
<span>Handoff viewer</span>
<small>The operator surface that renders handoffs with full context.</small>
</a>

</div>
