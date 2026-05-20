# Adjacent-tool migration assessment

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `AdjacentToolMapping` and
`AdjacentToolMigrationAssessment` contracts that describe how
concepts from nearby tools map into Craik before an importer is built.

</div>

<div className="craik-keypoint">

**Assessment, not import.**

An assessment is an evidence-backed compatibility record that can
later feed import dry-run reports, migration maps, and bridge
decisions.

</div>

## Records

<div className="craik-fields">

<div>
<dt>Contract</dt>
<dt><span className="craik-fields__type">Records</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>AdjacentToolMapping</code></dt>
<dt><span className="craik-fields__type">per concept</span></dt>
<dd>Source concept · target Craik concept (<code>project</code> / <code>task</code> / <code>memory</code> / <code>skill</code> / <code>config</code> / <code>receipt</code>) · support level (<code>supported</code> / <code>partial</code> / <code>unsupported</code>) · notes · required controls · unsupported fields.</dd>
</div>

<div>
<dt><code>AdjacentToolMigrationAssessment</code></dt>
<dt><span className="craik-fields__type">per tool</span></dt>
<dd>Assessment id · tool name · overall support level · mappings · security notes · redaction requirement · policy envelope id · evidence ids · receipt ids.</dd>
</div>

</div>

## Compatibility

<div className="craik-decision">

<div>
<h4>Supported</h4>
<p>Can be converted without losing Craik's policy, evidence, receipt, and redaction model.</p>
</div>

<div>
<h4>Partial</h4>
<p>Needs operator review. Unsupported fields must be named so a dry run can warn without mutating state.</p>
</div>

<div>
<h4>Unsupported</h4>
<p>Should not be imported. Secrets and credentials should be reconfigured by an operator, not copied.</p>
</div>

</div>

## What's next

<div className="craik-next">

<a href="import-dry-run/">
<strong>Reference</strong>
<span>Import dry-run reports</span>
<small>How an assessment becomes a reviewable dry run.</small>
</a>

<a href="migration-maps/">
<strong>Reference</strong>
<span>Migration maps</span>
<small>Field-level mapping for memory, skill, and config imports.</small>
</a>

<a href="adjacent-runtime-bridge/">
<strong>Reference</strong>
<span>Adjacent runtime bridge</span>
<small>The runtime-level bridge contract.</small>
</a>

</div>
