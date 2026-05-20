# Graph export

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `craik.work_graph_export` command surface — repository-wide and
task-scoped exports of nodes and edges from the local work graph.

</div>

<div className="craik-keypoint">

**Derived from local-store contracts.**

Graph export currently derives from local store contracts. Future
runtime workflows can add more `craik.work_graph_event` records to
connect delegated work, external artifacts, and review decisions.

</div>

## Commands

<div className="craik-fields">

<div>
<dt>Command</dt>
<dt><span className="craik-fields__type">Scope</span></dt>
<dd>Output</dd>
</div>

<div>
<dt><code>craik graph export</code></dt>
<dt><span className="craik-fields__type">repo-wide</span></dt>
<dd>All graph-compatible local objects in the current Craik home.</dd>
</div>

<div>
<dt><code>craik graph export --task-id &lt;id&gt;</code></dt>
<dt><span className="craik-fields__type">task-scoped</span></dt>
<dd>Connected local objects for the requested task.</dd>
</div>

</div>

## Payload shape

`craik.work_graph_export`:

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Contents</dd>
</div>

<div>
<dt><code>nodes</code></dt>
<dt><span className="craik-fields__type">list</span></dt>
<dd><code>id</code> · <code>type</code> · <code>label</code> · optional <code>task_id</code> · redacted metadata.</dd>
</div>

<div>
<dt><code>edges</code></dt>
<dt><span className="craik-fields__type">list</span></dt>
<dd><code>id</code> · <code>type</code> · <code>from</code> · <code>to</code> · redacted metadata.</dd>
</div>

</div>

## What's next

<div className="craik-next">

<a href="../schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The <code>work_graph_export</code> shape in the schema catalog.</small>
</a>

<a href="../operator-surface/">
<strong>Reference</strong>
<span>Operator surface</span>
<small>The work-graph explorer view that consumes exports.</small>
</a>

<a href="../local-store/">
<strong>Reference</strong>
<span>Local store</span>
<small>Where the exported records live.</small>
</a>

</div>
