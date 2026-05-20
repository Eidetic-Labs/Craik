# Context budgeting

<p className="craik-meta"><span>3 min read</span><span>For operators &amp; agents</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Use the case-file context budget to bound what reaches a runner. The
local assembler records what was included, omitted, and excluded —
agents can see the boundary instead of guessing.

</div>

<div className="craik-keypoint">

**Omissions are visible by design.**

When docs are omitted, the assembler adds an open assumption so the
next agent sees the case file is incomplete.

</div>

## Build with the default budget

```sh
craik case build task_review_docs
```

Set a smaller or larger approximate token budget:

```sh
craik case build task_review_docs --max-tokens 12000
```

## What the assembler records

<div className="craik-grid">

<div><h4><code>max_tokens</code></h4></div>
<div><h4><code>estimated_tokens</code></h4></div>
<div><h4><code>docs_included</code></h4></div>
<div><h4><code>adrs_included</code></h4></div>
<div><h4><code>docs_omitted</code></h4></div>
<div><h4><code>docs_excluded</code></h4></div>
<div><h4><code>discovery_rules</code></h4></div>
<div><h4><code>evidence_count</code></h4></div>
<div><h4><code>assumption_count</code></h4></div>

</div>

## Default discovery exclusions

Craik applies repository discovery defaults before budgeting.
Generated, dependency, build, cache, and archive-heavy paths are
excluded by default so a case file does not spend context on paths
such as `node_modules/`, `docs/build/`, or `docs/archive/`.

## Project rules

Persist project-level discovery rules at registration time:

```sh
craik project add /path/to/repo \
  --discovery-exclude "docs/generated/**" \
  --discovery-include "docs/archive/current-release/**"
```

## Per-build overrides

Apply one-off user overrides when building a case file:

```sh
craik case build task_review_docs \
  --discovery-exclude "docs/drafts/**" \
  --discovery-include "docs/archive/current-release/**"
```

<div className="craik-decision">

<div>
<h4>Include rules</h4>
<p>Restore matching paths even when a default exclude would normally skip them.</p>
</div>

<div>
<h4>Exclude rules</h4>
<p>Add to the default exclusions.</p>
</div>

</div>

Excluded paths are reported in `context_budget.docs_excluded` with the
matching rule so an agent can see what was skipped and why.

<div className="craik-keypoint">

**Conservative path-based estimator.**

The current estimator is intentionally conservative and path-based.
Later case-assembly work will replace it with content-aware budgeting
as repo, memory, GitHub, and handoff adapters mature.

</div>

## What's next

<div className="craik-next">

<a href="../using-case-files/">
<strong>Guide</strong>
<span>Using case files</span>
<small>Read the assembled case-file structure.</small>
</a>

<a href="../scope-control/">
<strong>Guide</strong>
<span>Scope control</span>
<small>Intent locks and stop-conditions for bounded runs.</small>
</a>

<a href="../../reference/context-debt/">
<strong>Reference</strong>
<span>Context debt</span>
<small>The contract that records paths skipped or omitted.</small>
</a>

</div>
