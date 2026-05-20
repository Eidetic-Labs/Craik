# Migration maps

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The two contracts that describe how source fields become Craik fields
during memory, skill, and config imports — `MigrationFieldMap` and
`MigrationMap`.

</div>

<div className="craik-keypoint">

**Importers use maps during dry runs before mutating state.**

Supported fields can be transformed. Partial fields require operator
review. Unsupported fields must remain out of imported records.

</div>

## Records

<div className="craik-fields">

<div>
<dt>Contract</dt>
<dt><span className="craik-fields__type">Records</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>MigrationFieldMap</code></dt>
<dt><span className="craik-fields__type">per field</span></dt>
<dd>Source field · target Craik field · support level (<code>supported</code> / <code>partial</code> / <code>unsupported</code>) · transformation notes · redaction requirement · unsupported reason.</dd>
</div>

<div>
<dt><code>MigrationMap</code></dt>
<dt><span className="craik-fields__type">per surface</span></dt>
<dd>Map id · surface (<code>memory</code> / <code>skill</code> / <code>config</code>) · source name · field maps · compatibility notes · policy envelope id · evidence ids · receipt ids.</dd>
</div>

</div>

## Boundary

<div className="craik-keypoint">

**Secrets stay outside imports.**

Secrets, credentials, private payloads, and local-only paths should be
marked unsupported or redacted — not copied.

</div>

Migration maps preserve policy, evidence, and receipt links so future
importers can explain why a field was transformed, skipped, or
blocked.

## What's next

<div className="craik-next">

<a href="import-dry-run/">
<strong>Reference</strong>
<span>Import dry-run reports</span>
<small>The dry-run report shape that consumes a map.</small>
</a>

<a href="adjacent-tool-migration/">
<strong>Reference</strong>
<span>Adjacent-tool migration</span>
<small>The assessment that defines mapping support per concept.</small>
</a>

<a href="secret-migration-policy/">
<strong>Reference</strong>
<span>Secret migration policy</span>
<small>Why secrets stay outside imports.</small>
</a>

</div>
