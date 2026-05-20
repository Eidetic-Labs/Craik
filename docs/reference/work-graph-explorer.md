# Work graph explorer

<p className="craik-meta"><span>2 min read</span><span>Reference · preview</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The read-only operator view over `craik.work_graph_export` and
`craik.work_graph_event` records — what it formats and the boundary
that keeps it inspection-only.

</div>

<div className="craik-keypoint">

**No graph mutation.**

The explorer reads exported graph records and graph events from the
local store and displays missing data as an empty graph or absent
metadata.

</div>

## What it formats

<div className="craik-grid">

<div><h4>Graph id and task scope</h4></div>
<div><h4>Node count and edge count</h4></div>
<div><h4>Node rows</h4><p>Id · type · task · label.</p></div>
<div><h4>Edge rows</h4><p>Source · relationship type · target · sorted metadata.</p></div>

</div>

The explorer should help operators scan dependencies, blockers,
contradictions, supersession, implementation links, and verification
links without reading raw logs.

## What's next

<div className="craik-next">

<a href="graph-export/">
<strong>Reference</strong>
<span>Graph export</span>
<small>The export command this view reads.</small>
</a>

<a href="operator-surface/">
<strong>Reference</strong>
<span>Operator surface</span>
<small>The shared TUI boundary.</small>
</a>

<a href="schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>The <code>work_graph_export</code> and <code>work_graph_event</code> shapes.</small>
</a>

</div>
