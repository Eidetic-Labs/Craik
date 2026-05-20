# Scope Control

<p className="craik-meta"><span>5 min read</span><span>For operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Configure explicit scope controls on a task so the runtime's intent lock
keeps execution aligned with the accepted request. By the end you'll know
how to set in-scope and out-of-scope items, allowed autonomy, stop
conditions, and scope-change rules — and when to refresh them mid-run.

</div>

## The pattern

Craik uses [intent locks](../concepts/intent-locks.md) to keep task
execution honest. Scope control is how you configure the lock at task
creation time:

```bash title="A task with explicit scope"
craik task create \
  --project Example \
  --title "Review docs" \
  --objective "Review docs against implementation." \
  --accepted-interpretation "Review documentation only." \
  --in-scope "README.md" \
  --in-scope "docs/" \
  --out-of-scope "ADR edits" \
  --allowed-autonomy "Inspect repository files" \
  --stop-condition "The task requires changing immutable docs" \
  --scope-change-rule "Ask before expanding beyond documentation review"
```

Then inspect the lock the runtime accepted:

```bash title="Read what got accepted"
craik intent show task_review_docs
```

## The six knobs

<div className="craik-fields">

<div>
<dt>Flag</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>--accepted-interpretation</code></dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>The runtime's plain-language understanding of the task. Where ambiguity gets named.</dd>
</div>

<div>
<dt><code>--in-scope</code></dt>
<dt><span className="craik-fields__type">item (repeatable)</span></dt>
<dd>Concrete work the run is allowed to perform.</dd>
</div>

<div>
<dt><code>--out-of-scope</code></dt>
<dt><span className="craik-fields__type">item (repeatable)</span></dt>
<dd>Explicit forbidden actions. The runner must stop or ask before crossing one.</dd>
</div>

<div>
<dt><code>--allowed-autonomy</code></dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>How far the runner may go without checking in.</dd>
</div>

<div>
<dt><code>--stop-condition</code></dt>
<dt><span className="craik-fields__type">condition (repeatable)</span></dt>
<dd>Conditions that should halt the run pending review.</dd>
</div>

<div>
<dt><code>--scope-change-rule</code></dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>How the runner should request a scope update if the lock doesn't fit.</dd>
</div>

</div>

## Conservative defaults

If you skip the scope flags, Craik creates conservative defaults from the
task request:

<div className="craik-grid">

<div>
<h4>Title becomes the original request</h4>
<p>The verbatim user input is preserved as the lock's <code>original_request</code>.</p>
</div>

<div>
<h4>Objective becomes the accepted interpretation</h4>
<p>If you didn't name a separate interpretation, the objective stands in.</p>
</div>

<div>
<h4>Expected outputs become in-scope work</h4>
<p>What the task said it would produce defines what's allowed.</p>
</div>

<div>
<h4>Constraints become out-of-scope work</h4>
<p>Any declared constraint flips to a forbidden action.</p>
</div>

<div>
<h4>Stop conditions are non-empty by default</h4>
<p>Default stops fire when project context is missing, policy conflicts arise, or the objective materially changes.</p>
</div>

</div>

Defaults are a floor, not a ceiling. Explicit flags always win when present.

## Review before authorizing

Before letting a run proceed, read the lock and confirm:

<ol className="craik-steps">
<li>

**`accepted_interpretation` matches reality.** If the runtime understood
something different from what you meant, fix it now.

</li>
<li>

**`in_scope` is concrete and narrow.** Vague items like "improve docs"
invite drift; "update docs/architecture.md to reflect runtime state"
doesn't.

</li>
<li>

**`out_of_scope` names obvious traps.** ADR edits, schema migrations,
secret rotations — call them out by name.

</li>
<li>

**`allowed_autonomy` matches your trust.** Inspection-only runs should
*not* declare "execute shell commands" as allowed.

</li>
<li>

**`stop_conditions` cover known risk.** Anything you'd want to pause for
should be a stop condition, not a hope.

</li>
<li>

**`scope_change_rules` tell the runner how to ask.** When the lock
doesn't fit, the runner needs a documented escape hatch.

</li>
</ol>

## When to update mid-run

If the runner finds work that crosses the lock, it should **pause and
ask** — not silently widen scope. To update the intent lock mid-run:

<div className="craik-cmd">
<code>craik intent update task_review_docs --in-scope "docs/architecture.md edits"</code>
<p>Updates the lock with a new in-scope item. The change is recorded for audit.</p>
</div>

The original `accepted_interpretation` stays preserved. Updates are
additive history, not replacements — you can audit the full trajectory of
how the lock evolved during a task.

## What to do when stop conditions fire

A stop condition firing is not a failure — it's the runtime working as
designed. The right responses, in order:

<div className="craik-decision">

<div>
<h4>Stop, review, decide</h4>
<ul>
<li>Inspect what the runner produced up to the stop point.</li>
<li>Decide: widen the lock, change the policy envelope, or end the task.</li>
<li>Record the decision in the next handoff's <code>policy_exceptions</code>.</li>
</ul>
</div>

<div>
<h4>Don't ignore</h4>
<ul>
<li>Don't disable a stop condition without writing down why.</li>
<li>Don't restart the run hoping it won't trip the condition again — fix the underlying issue.</li>
<li>Don't widen autonomy as a workaround for a recurring stop.</li>
</ul>
</div>

</div>

## What's next

<div className="craik-next">

<a href="../../concepts/intent-locks/">
<strong>Read</strong>
<span>Intent locks</span>
<small>The typed object you're configuring with these flags.</small>
</a>

<a href="../capability-grants/">
<strong>Do</strong>
<span>Capability grants</span>
<small>Pair tight intent locks with narrow capability grants for double-belt-and-suspenders.</small>
</a>

<a href="../writing-handoffs/">
<strong>Do</strong>
<span>Write a handoff</span>
<small>Record scope changes and stops in the handoff's policy exceptions.</small>
</a>

</div>
