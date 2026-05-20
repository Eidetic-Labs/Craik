# Multi-agent workflow migration assessment

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `MultiAgentWorkflowMapping` and
`MultiAgentWorkflowMigrationAssessment` contracts that describe how
external workflow systems map into Craik before bridges or importers
are built.

</div>

<div className="craik-keypoint">

**Assessment, not bridge.**

Records migration compatibility and risks so later dry runs, migration
maps, and bridge decisions stay reviewable.

</div>

## Records

<div className="craik-fields">

<div>
<dt>Contract</dt>
<dt><span className="craik-fields__type">Records</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>MultiAgentWorkflowMapping</code></dt>
<dt><span className="craik-fields__type">per concept</span></dt>
<dd>Source concept · target workflow concept (<code>agent</code> / <code>role</code> / <code>queue</code> / <code>artifact</code> / <code>memory</code> / <code>approval</code>) · target Craik surface · support level (<code>supported</code> / <code>partial</code> / <code>unsupported</code>) · notes · required controls · unsupported fields.</dd>
</div>

<div>
<dt><code>MultiAgentWorkflowMigrationAssessment</code></dt>
<dt><span className="craik-fields__type">per workflow</span></dt>
<dd>Assessment id · workflow name · overall support level · mappings · policy notes · redaction requirement · policy envelope id · evidence ids · receipt ids.</dd>
</div>

</div>

## Compatibility

<div className="craik-decision">

<div>
<h4>Supported mappings</h4>
<ul>
<li>Agents &amp; roles → Craik agent roles when authority is explicit</li>
<li>Queues → delegation queues when dispatch, ownership, receipts, and review are bounded</li>
<li>Artifacts, memories, approvals → preserve evidence, receipt, policy, redaction semantics</li>
</ul>
</div>

<div>
<h4>Unsupported</h4>
<ul>
<li>Unbounded autonomous queues</li>
<li>Hidden side effects</li>
<li>Raw private artifacts</li>
<li>Approval steps without receipts</li>
</ul>
</div>

</div>

## What's next

<div className="craik-next">

<a href="../multi-agent-workflow-bridge/">
<strong>Reference</strong>
<span>Multi-agent workflow bridge</span>
<small>The bridge that follows an assessment.</small>
</a>

<a href="../import-dry-run/">
<strong>Reference</strong>
<span>Import dry-run reports</span>
<small>How an assessment becomes a reviewable dry run.</small>
</a>

<a href="../agent-roles/">
<strong>Reference</strong>
<span>Agent roles</span>
<small>The roles external agents map to.</small>
</a>

</div>
