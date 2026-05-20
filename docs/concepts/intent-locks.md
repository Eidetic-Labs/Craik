# Intent Locks

<p className="craik-meta"><span>5 min read</span><span>Core concept</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- What an intent lock is and why every task gets one.
- The split between the user's request and the runtime's accepted interpretation.
- When a runner should pause for a scope update vs. continue.
- How locks integrate with case files, handoffs, and the work graph.

</div>

<div className="craik-keypoint">

**Intent lock**

The runtime's accepted interpretation of a task — explicit, durable, and
separate from the original request. The lock declares what's in scope,
what's out of scope, how much autonomy the runner has, and what conditions
should stop the run.

</div>

## Why bother?

Long-running agent work drifts. Mid-run, a new finding makes a nearby
change tempting. A tool returns output that implies "I should also fix
this related thing." Partial progress nudges the runner toward "while I'm
here, let me clean up..." Each step in isolation looks reasonable; the
cumulative effect is scope creep that nobody approved.

Intent locks make that drift **visible and reviewable**. The lock is what
the runtime committed to before the work began — every later decision can
be checked against it.

## What a lock records

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt>original_request</dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>The user's words. Preserved verbatim — never edited to "make the runtime sound smarter."</dd>
</div>

<div>
<dt>objective</dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>The runtime's short statement of what success looks like.</dd>
</div>

<div>
<dt>accepted_interpretation</dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>How the runtime understood the request. The interesting field — this is where ambiguity gets named.</dd>
</div>

<div>
<dt>in_scope</dt>
<dt><span className="craik-fields__type">item[]</span></dt>
<dd>Concrete work the run is allowed to perform.</dd>
</div>

<div>
<dt>excluded</dt>
<dt><span className="craik-fields__type">item[]</span></dt>
<dd>Explicit out-of-scope items. The runner must stop or ask before touching these.</dd>
</div>

<div>
<dt>allowed_autonomy</dt>
<dt><span className="craik-fields__type">level</span></dt>
<dd>How far the runner may go without checking in — file edits, shell, GitHub writes, memory.write, etc.</dd>
</div>

<div>
<dt>stop_conditions</dt>
<dt><span className="craik-fields__type">condition[]</span></dt>
<dd>Trigger conditions that should halt the run pending operator review.</dd>
</div>

<div>
<dt>scope_change_rules</dt>
<dt><span className="craik-fields__type">rule</span></dt>
<dd>How the runner should request a scope update if the lock doesn't fit.</dd>
</div>

</div>

The lock persists as a `craik.intent_lock` record and is referenced from
the matching case file and every subsequent handoff. Handoff contracts
include an intent-lock field so future handoff writers can preserve the
same boundary across runs.

## When a runner should pause

<ol className="craik-steps">
<li>

**The requested work no longer matches the accepted interpretation.**
Mid-run discovery: the user really meant something narrower or wider.
Stop and ask for a lock update.

</li>
<li>

**A required action is listed as out of scope.** The runner identifies
a step it would have to take to finish, but `excluded` forbids it. Stop
and ask.

</li>
<li>

**The task would cross a stop condition.** A stop condition fired
(reviewer required, budget exceeded, contradiction surfaced). Halt and
write a handoff that names what stopped the run.

</li>
<li>

**The task requires new autonomy not listed in the lock.** The runner
needs a capability the lock doesn't grant (e.g., wants to run a shell
command but `allowed_autonomy` doesn't include shell). Request the grant
or stop.

</li>
</ol>

## How locks compose with the rest of the runtime

Intent locks aren't a separate system — they're a typed object that other
parts of the runtime cite:

<div className="craik-grid">

<div>
<h4>Case files</h4>
<p>Every case file references its intent lock id, so the runner sees the boundary alongside the evidence and verification plan.</p>
</div>

<div>
<h4>Handoffs</h4>
<p>Handoffs reference the same lock id. The next agent picks up <em>with</em> the original boundary, not without it.</p>
</div>

<div>
<h4>Policy</h4>
<p>The policy envelope and the intent lock together describe what's permitted. The lock declares scope; the envelope declares capability.</p>
</div>

<div>
<h4>Work graph</h4>
<p>Locks are queryable nodes — useful when auditing how a task's interpretation evolved across multiple runs.</p>
</div>

</div>

## Use intent locks day-to-day

<div className="craik-cmd">
<code>craik task create --out-of-scope "ADR edits" --out-of-scope "schema migrations"</code>
<p>The task-creation command produces the matching intent lock from the flags you pass.</p>
</div>

<div className="craik-cmd">
<code>craik intent show task_review_docs</code>
<p>Print the lock by task id or intent-lock id. Useful for review before authorizing a run.</p>
</div>

<div className="craik-cmd">
<code>craik case build task_review_docs</code>
<p>Ensures the task has an intent lock and includes its id in the resulting case file.</p>
</div>

## Why locks are separate from the request

It's tempting to skip locks and just "do what the user asked." That conflates
two distinct things:

- **What the user said** — preserved as `original_request`.
- **What the runtime committed to do about it** — the lock.

When those two diverge — and they do, often — having both addressable
makes review tractable. You can ask: *"Did the runtime's accepted
interpretation match what the user actually wanted?"* and have a
machine-readable answer.

## What's next

<div className="craik-next">

<a href="../../guides/scope-control/">
<strong>Do</strong>
<span>Scope control</span>
<small>Patterns for keeping intent locks tight and updating them safely.</small>
</a>

<a href="../case-files/">
<strong>Read</strong>
<span>Case files</span>
<small>How locks compose with the per-task case file.</small>
</a>

<a href="../handoffs/">
<strong>Read</strong>
<span>Handoffs</span>
<small>How locks travel across runs via the handoff contract.</small>
</a>

</div>
