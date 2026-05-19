# Using Case Files

<p className="craik-meta"><span>6 min read</span><span>For operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Build, inspect, and refresh per-task case files day-to-day. By the end you'll
know how to tune discovery for one project or one run, what fields to review
before authorizing work, and how to keep case-file context honest.

</div>

## Prerequisites

- A registered project (see [Project registry](project-registry.md)).
- A task created with `craik task create`. The case-file build pulls the
  task's objective and intent lock.

## 1 · Register the project with the right boundaries

Case files are only as good as the project they're built against. Tune
discovery during registration:

```bash title="Register a project with explicit boundaries"
craik project add /path/to/repo \
  --name Example \
  --docs-path README.md \
  --docs-path docs/ \
  --immutable-path docs/adr/
```

When the default repository discovery rules need project-specific tuning,
add `--discovery-exclude` / `--discovery-include`:

```bash title="Exclude generated docs; keep archived release notes"
craik project add /path/to/repo \
  --name Example \
  --discovery-exclude "docs/generated/**" \
  --discovery-include "docs/archive/current-release/**"
```

## 2 · Create the task

```bash title="A reviewable task with explicit scope"
craik task create \
  --project Example \
  --title "Review docs" \
  --objective "Review docs against implementation." \
  --mode review \
  --out-of-scope "ADR edits"
```

The `--out-of-scope` flag rolls into the intent lock, which the case file
will reference.

## 3 · Build the case file

```bash title="Default build"
craik case build task_review_docs
```

For a single run, override discovery without changing the project:

```bash title="One-off discovery override"
craik case build task_review_docs --discovery-exclude "docs/drafts/**"
```

## 4 · Inspect what you got

```bash title="Show by task id or case-file id"
craik case show task_review_docs
craik case show case_review_docs
```

The output is structured JSON. Pipe it through `jq` or your editor. The
fields you should always read before authorizing a run:

<div className="craik-grid">

<div>
<h4><code>objective</code></h4>
<p>The runtime's stated goal for the task. Match it against what you actually want.</p>
</div>

<div>
<h4><code>policy_envelope_id</code></h4>
<p>The policy that will gate execution. Confirm it matches the run's risk profile.</p>
</div>

<div>
<h4><code>intent_lock_id</code></h4>
<p>The scope contract — in/out-of-scope, stop conditions, allowed autonomy.</p>
</div>

<div>
<h4><code>repo_state</code></h4>
<p>Branch, head, clean/dirty status. Make sure you're on the branch you think you are.</p>
</div>

<div>
<h4><code>docs</code></h4>
<p>Mutable doc roots that will be loaded as context.</p>
</div>

<div>
<h4><code>immutable_docs</code></h4>
<p>ADRs and other immutable evidence — read but not editable.</p>
</div>

<div>
<h4><code>evidence</code></h4>
<p>Every piece of context with its provenance. Spot-check that the evidence supports the task.</p>
</div>

<div>
<h4><code>assumptions</code></h4>
<p>What the runtime <em>couldn't</em> find. Open assumptions are not bugs — they're honesty.</p>
</div>

<div>
<h4><code>stale_risks</code></h4>
<p>Markers calling out context the runtime believes may have moved since indexing.</p>
</div>

<div>
<h4><code>context_budget</code></h4>
<p>Deterministic per-section token allocations. <code>context_budget.docs_excluded</code> lists generated / dependency / build / cache / archive paths skipped before budgeting.</p>
</div>

</div>

`context_budget.docs_excluded` is worth attention: if a path you expected
to be included is listed there, you probably want a `--discovery-include`
override for either the project or this specific build.

## 5 · Treat assumptions as first-class

Open assumptions mean the case file is **useful but incomplete**. The
runtime is being honest about what it couldn't find — typically because
a memory backend isn't configured, the GitHub adapter is off, or evidence
expected from a prior handoff is missing.

Downstream agents should:

<ol className="craik-steps">
<li>

**Keep assumptions visible** in plans, findings, and handoffs.

</li>
<li>

**Not promote assumptions to facts** without evidence.

</li>
<li>

**Surface unresolved assumptions** in the eventual handoff's
`assumptions` field so the next run inherits them.

</li>
</ol>

## Refreshing a case file

Case files are sealed once built — Craik won't silently rewrite one. To
refresh context for a re-run, build a *new* case file. The old one stays
addressable for audit:

```bash title="Build a new case file for the same task"
craik case build task_review_docs
craik case show task_review_docs   # shows the latest by default
```

## Common patterns

<div className="craik-decision">

<div>
<h4>"This case file looks thin."</h4>
<ul>
<li>Check <code>context_budget.docs_excluded</code> — likely an over-aggressive default exclude.</li>
<li>Confirm <code>memory_backend</code> is configured if you expected memory facts.</li>
<li>Confirm the GitHub adapter is wired in if you expected issue/PR context.</li>
</ul>
</div>

<div>
<h4>"This case file is loading too much."</h4>
<ul>
<li>Add a <code>--discovery-exclude</code> override for the project or this build.</li>
<li>Mark vendored / generated paths as immutable so they're loaded as evidence (not as mutable docs).</li>
<li>Check whether assumptions are blowing up the budget — they shouldn't, but pathological cases happen.</li>
</ul>
</div>

</div>

## What's next

<div className="craik-next">

<a href="../writing-handoffs/">
<strong>Do next</strong>
<span>Write a handoff</span>
<small>Close the loop — turn the case-file context into a continuity record.</small>
</a>

<a href="../../concepts/case-files/">
<strong>Read</strong>
<span>Case-file concept</span>
<small>The typed-object view of what you just built.</small>
</a>

<a href="../../reference/local-state/">
<strong>Reference</strong>
<span>Local state layout</span>
<small>Where case files persist on disk.</small>
</a>

</div>
