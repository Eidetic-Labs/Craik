# Import dry-run reports

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The three records that compose a dry-run report — candidate records,
mapped records, and the assembled report — plus the boundary that
keeps dry runs from mutating state.

</div>

<div className="craik-keypoint">

**Compatibility report, not a write.**

Dry runs do not write tasks, memory, skills, config, receipts, or
artifacts. They are compatibility reports for operator review.

</div>

## Records

<div className="craik-fields">

<div>
<dt>Record</dt>
<dt><span className="craik-fields__type">Captures</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>ImportCandidateRecord</code></dt>
<dt><span className="craik-fields__type">per source</span></dt>
<dd>Source id · source type · redacted summary · redaction status.</dd>
</div>

<div>
<dt><code>ImportMappedRecord</code></dt>
<dt><span className="craik-fields__type">per mapping</span></dt>
<dd>Source id · target schema · target id · status (<code>mapped</code> / <code>warning</code> / <code>error</code> / <code>unsupported</code>) · warnings · errors.</dd>
</div>

<div>
<dt><code>ImportDryRunReport</code></dt>
<dt><span className="craik-fields__type">per dry run</span></dt>
<dd>Source name &amp; kind · candidate records · mapped records · warnings · errors · <code>mutated_state: false</code> · redaction status · policy envelope id · evidence ids · receipt ids.</dd>
</div>

</div>

## Boundary

<div className="craik-keypoint">

**Warnings vs. errors.**

Warnings indicate records needing review before import. Errors and
unsupported mappings prevent import until the source data or migration
map is changed.

</div>

Dry-run reports preserve policy, evidence, and receipt links so
migration decisions remain auditable.

## What's next

<div className="craik-next">

<a href="migration-maps/">
<strong>Reference</strong>
<span>Migration maps</span>
<small>The field-level mapping dry runs consume.</small>
</a>

<a href="adjacent-tool-migration/">
<strong>Reference</strong>
<span>Adjacent-tool migration</span>
<small>The assessment that precedes a dry run.</small>
</a>

<a href="secret-migration-policy/">
<strong>Reference</strong>
<span>Secret migration policy</span>
<small>Why secrets stay outside imports.</small>
</a>

</div>
