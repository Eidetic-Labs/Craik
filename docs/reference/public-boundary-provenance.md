# Public boundary and provenance

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The machine-checkable MVP boundary that keeps Craik public docs free
of private paths, raw credentials, internal-only labels, and local
secret filenames — plus the hygiene scanner and provenance helpers.

</div>

<div className="craik-keypoint">

**Public docs are policed.**

`craik.runtime.projects.public_docs` provides the machine-checkable
boundary; <code>scripts/check_public_docs_hygiene.py</code> runs in
the CI security gate.

</div>

## Classification

<div className="craik-fields">

<div>
<dt>Class</dt>
<dt><span className="craik-fields__type">Covers</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>public</code></dt>
<dt><span className="craik-fields__type">shipped</span></dt>
<dd>README · changelog · Docusaurus docs.</dd>
</div>

<div>
<dt><code>internal</code></dt>
<dt><span className="craik-fields__type">repo</span></dt>
<dd>Source · tests · scripts · CI · unclassified repository work.</dd>
</div>

<div>
<dt><code>private</code></dt>
<dt><span className="craik-fields__type">local</span></dt>
<dd>Local state · secret paths · user-specific runtime files.</dd>
</div>

</div>

## Hygiene

`scripts/check_public_docs_hygiene.py` scans public docs for obvious
leaks. The CI security gate runs it with release-readiness and policy
tests.

## Provenance

<div className="craik-keypoint">

**Generated docs cite source.**

<code>generated_doc_provenance</code> creates
<code>craik.evidence_reference</code> records that link generated docs
back to source files, tests, or commands.

</div>

## Staleness

`stale_documentation_findings` compares generated docs against source
mtimes and returns stale-risk findings when a source is newer than the
generated doc.

<div className="craik-keypoint">

**Repeat findings → decision records.**

Repeated boundary findings should produce decision records for path
redaction, secret handling, or task naming.

</div>

## What's next

<div className="craik-next">

<a href="../redaction/">
<strong>Reference</strong>
<span>Redaction</span>
<small>The persistence-time redaction utility.</small>
</a>

<a href="../../security/release-process/">
<strong>Security</strong>
<span>Release process</span>
<small>How public boundary findings interact with releases.</small>
</a>

<a href="../failure-modes/">
<strong>Reference</strong>
<span>Failure modes</span>
<small>How the hygiene gate composes with the wider failure posture.</small>
</a>

</div>
