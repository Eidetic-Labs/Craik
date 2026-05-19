# Work Graph

<p className="craik-meta"><span>5 min read</span><span>Core concept</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- What the work graph is and why it exists.
- The node types and edge types Craik connects.
- How to export the graph, what's redacted, and what it can and can't do.
- How the graph is queried by operator views and downstream tooling.

</div>

<div className="craik-keypoint">

**Work graph**

The connected, queryable view of runtime objects that would otherwise be
scattered across case files, receipts, handoffs, memory proposals, evidence,
assumptions, and contradictions.

The graph isn't a separate data store — it's a *projection* over the existing
typed objects in `$CRAIK_HOME/state/`. Every node and edge is derivable from
the records Craik already keeps.

</div>

## Why a graph?

Tasks don't end in one act. A real piece of agent work produces:

- A **case file** built from project state, evidence, and assumptions.
- One or more **receipts** as the runtime takes governed actions.
- A **handoff** that closes (or pauses) the run and proposes memory.
- Sometimes a **contradiction** when new facts collide with old ones.
- Sometimes a **memory proposal** that needs reviewer approval.

These pieces only become useful when you can ask cross-cutting questions:
*"Which receipts contributed to this handoff?"* · *"Which case files cite
this ADR as evidence?"* · *"Which contradictions are still open against
this project?"*

The work graph is what makes those questions tractable.

## Node types

<div className="craik-grid">

<div>
<h4><code>task</code></h4>
<p>A unit of work with an objective and an intent lock.</p>
</div>

<div>
<h4><code>case_file</code></h4>
<p>The per-task pre-run brief — evidence, assumptions, verification plan.</p>
</div>

<div>
<h4><code>handoff</code></h4>
<p>The post-run continuity record. One per task per run.</p>
</div>

<div>
<h4><code>receipt</code></h4>
<p>A capability receipt for a governed action.</p>
</div>

<div>
<h4><code>memory_proposal</code></h4>
<p>A fact a run wants written to memory, pending review.</p>
</div>

<div>
<h4><code>fact</code></h4>
<p>An approved fact in memory — Stigmem or local memory backend.</p>
</div>

<div>
<h4><code>evidence</code></h4>
<p>An evidence reference: file, GitHub issue, prior handoff, memory fact.</p>
</div>

<div>
<h4><code>assumption</code></h4>
<p>An open or resolved assumption recorded in a case file or handoff.</p>
</div>

<div>
<h4><code>contradiction</code></h4>
<p>A surfaced conflict between facts, evidence, or assumptions.</p>
</div>

</div>

## Edge types

Edges explain how nodes relate. Common ones:

<div className="craik-fields">

<div>
<dt>Edge</dt>
<dt><span className="craik-fields__type">Direction</span></dt>
<dd>Meaning</dd>
</div>

<div>
<dt><code>has_case_file</code></dt>
<dt><span className="craik-fields__type">task → case_file</span></dt>
<dd>Every task has exactly one current case file.</dd>
</div>

<div>
<dt><code>has_receipt</code></dt>
<dt><span className="craik-fields__type">task → receipt</span></dt>
<dd>The receipts produced under the task's policy envelope.</dd>
</div>

<div>
<dt><code>records_receipt</code></dt>
<dt><span className="craik-fields__type">handoff → receipt</span></dt>
<dd>Receipts cited explicitly in a handoff's <code>receipts</code> list.</dd>
</div>

<div>
<dt><code>proposes_memory</code></dt>
<dt><span className="craik-fields__type">handoff → memory_proposal</span></dt>
<dd>Memory proposals emitted by the run.</dd>
</div>

<div>
<dt><code>supported_by</code></dt>
<dt><span className="craik-fields__type">proposal → evidence</span></dt>
<dd>The evidence backing a memory proposal.</dd>
</div>

<div>
<dt><code>contains_assumption</code></dt>
<dt><span className="craik-fields__type">case_file → assumption</span></dt>
<dd>Open assumptions a case file recorded.</dd>
</div>

<div>
<dt><code>contains_contradiction</code></dt>
<dt><span className="craik-fields__type">case_file → contradiction</span></dt>
<dd>Contradictions surfaced during case-file assembly.</dd>
</div>

<div>
<dt><code>resolves</code></dt>
<dt><span className="craik-fields__type">handoff → contradiction</span></dt>
<dd>Contradictions a run closed.</dd>
</div>

</div>

## Export the graph

```bash title="Export the work graph for a task"
craik graph export --task task_review_docs
```

```bash title="Export the full project graph"
craik graph export --project Example
```

The graph export emits a typed JSON payload by default, with a Graphviz
DOT export available for visualization tooling:

```bash title="DOT for Graphviz / d3 / Mermaid"
craik graph export --project Example --format dot
```

Output is **deterministic** — running export twice on the same state
produces byte-identical payloads. This makes the graph diffable in
review and stable for downstream consumers.

## What export is and isn't

<div className="craik-decision">

<div>
<h4>Graph export <strong>is</strong></h4>
<ul>
<li>Read-only. Never writes a fact, never mutates GitHub, never resolves a contradiction.</li>
<li>Deterministic. Same state → same bytes.</li>
<li>Redacted. Receipts and proposals are filtered through the same redaction guard the receipt store uses.</li>
<li>Joinable. Every node id is the same id you'd query in <code>craik receipts show</code>, <code>craik handoff show</code>, etc.</li>
</ul>
</div>

<div>
<h4>Graph export <strong>isn't</strong></h4>
<ul>
<li>Authority. Exporting the graph doesn't grant a capability.</li>
<li>A memory write. Memory still requires <code>memory.write</code> and the approval flow.</li>
<li>A side-effect channel. Nothing leaves the local store.</li>
<li>Hidden state. The export contains only what's already addressable in <code>$CRAIK_HOME/state/</code>.</li>
</ul>
</div>

</div>

## How operator views consume the graph

Several operator views are graph readers:

- **Work graph explorer** — full project graph with filtering.
- **Handoff viewer** — handoff plus the receipts, proposals, and
  assumptions it cites.
- **Receipt viewer** — receipt plus the task, policy, and handoffs it
  participates in.
- **Contradiction inbox** — open contradictions, the case files and
  facts they collide with, and the runs that surfaced them.

See [Reference · Operator surface](../reference/operator-surface.md) for the
full operator-view list.

## What's next

<div className="craik-next">

<a href="../handoffs/">
<strong>Read</strong>
<span>Handoffs</span>
<small>How a run closes and what it leaves for the next agent.</small>
</a>

<a href="../../reference/graph-export/">
<strong>Reference</strong>
<span>Graph export</span>
<small>Output shape, flags, and downstream consumer guidance.</small>
</a>

<a href="../../reference/work-graph-explorer/">
<strong>Reference</strong>
<span>Work graph explorer</span>
<small>The operator surface that renders the graph for review.</small>
</a>

</div>
