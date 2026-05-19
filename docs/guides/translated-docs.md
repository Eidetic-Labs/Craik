# Translated documentation strategy

<p className="craik-meta"><span>4 min read</span><span>For maintainers</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

How Craik handles localized docs. Translations are presentation
surfaces over the English source-of-truth pages. They never redefine
policy, evidence, receipt, redaction, schema, or identifier semantics.

</div>

<div className="craik-keypoint">

**Presentation, not policy.**

If a translation cannot preserve the meaning of a policy rule, schema
field, receipt status, or redaction requirement, the translated page
remains deferred and links back to the source page.

</div>

## Source of truth

Canonical documentation lives under `docs/` and is authored as the
source locale for each page. Translated pages may live in
locale-specific paths when reviewed and linked through metadata
described in
[Locale i18n framework](../reference/locale-i18n-framework.md).

Source-of-truth pages define:

<div className="craik-grid">

<div><h4>Stable language-neutral document ids</h4></div>
<div><h4>Canonical links</h4><p>To contracts and guides.</p></div>
<div><h4>Policy · evidence · receipt · redaction semantics</h4></div>
<div><h4>Public boundary requirements</h4></div>
<div><h4>Fallback path</h4><p>When a translation is unavailable.</p></div>

</div>

## Translation metadata

Each translatable page records:

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Required</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt>Stable document id</dt>
<dt><span className="craik-fields__type">always</span></dt>
<dd>Language-neutral identity.</dd>
</div>

<div>
<dt>Source path and source locale</dt>
<dt><span className="craik-fields__type">always</span></dt>
<dd>Canonical reference.</dd>
</div>

<div>
<dt>Available locales and translated paths</dt>
<dt><span className="craik-fields__type">always</span></dt>
<dd>Resolved at link time.</dd>
</div>

<div>
<dt>Policy envelope id</dt>
<dt><span className="craik-fields__type">always</span></dt>
<dd>Governs translation review.</dd>
</div>

<div>
<dt>Evidence references</dt>
<dt><span className="craik-fields__type">always</span></dt>
<dd>For source material and review.</dd>
</div>

<div>
<dt>Receipt references</dt>
<dt><span className="craik-fields__type">always</span></dt>
<dd>For translation checks.</dd>
</div>

<div>
<dt>Redaction requirement</dt>
<dt><span className="craik-fields__type">always</span></dt>
<dd>Applied to both source and translated pages.</dd>
</div>

<div>
<dt>Identifier-neutrality confirmation</dt>
<dt><span className="craik-fields__type">always</span></dt>
<dd>Runtime identifiers remain language-neutral.</dd>
</div>

</div>

This metadata is represented by `TranslatableDocMetadata` and resolved
through `resolve_doc_locale`. The resolution result records the
requested locale, resolved locale, fallback chain, path, and
policy/evidence/receipt context.

## Fallback links

Translated docs include a path back to the source page when a locale
is incomplete, stale, community-maintained, or deferred.

<ol className="craik-steps">
<li>Exact locale.</li>
<li>Language-only locale when configured.</li>
<li>Configured fallback locales.</li>
<li>Source locale.</li>
</ol>

<div className="craik-keypoint">

**Fallback links go to public pages only.**

Never expose local filesystem paths, private planning labels,
credentials, or private task names through fallback link resolution.

</div>

## Review expectations

<ol className="craik-steps">
<li>Public boundary language is preserved.</li>
<li>Redaction markers and secret references are not translated into secret values.</li>
<li>Schema names, ids, receipt ids, policy ids, memory entities, and task ids are unchanged.</li>
<li>Code blocks and CLI commands remain technically valid.</li>
<li>Links resolve through docs tests or documented deferred status.</li>
<li>Any machine-generated translation has human or policy review before being marked supported.</li>
</ol>

Review receipts record the source page, target locale, review
evidence, reviewer or automation id, and whether
policy/evidence/receipt/redaction semantics were preserved.

## Deferred and community-maintained translations

<div className="craik-decision">

<div>
<h4>Deferred</h4>
<p>No reviewer · terminology unsettled · source docs changing too quickly. Deferred translations use fallback links rather than stale translated prose.</p>
</div>

<div>
<h4>Community-maintained</h4>
<p>Acceptable when following the same metadata, review, public-boundary, and receipt expectations. Community status must be visible in the metadata or review receipt. Source docs remain authoritative when conflicts appear.</p>
</div>

</div>

## Limits

<div className="craik-keypoint">

**Translations must NOT.**

</div>

<div className="craik-grid">

<div><h4>Translate runtime identifiers</h4><p>Or schema names.</p></div>
<div><h4>Weaken policy / approval / grant / receipt / evidence / redaction</h4></div>
<div><h4>Introduce examples</h4><p>With real credentials, private paths, or private task names.</p></div>
<div><h4>Imply unsupported behavior</h4><p>Locale-specific behavior that does not exist in the runtime.</p></div>
<div><h4>Bypass docs link validation</h4><p>Except through explicitly documented deferred status.</p></div>

</div>

## What's next

<div className="craik-next">

<a href="../../reference/locale-i18n-framework/">
<strong>Reference</strong>
<span>Locale i18n framework</span>
<small>The metadata and resolution contracts.</small>
</a>

<a href="../../reference/translated-docs-strategy/">
<strong>Reference</strong>
<span>Translated docs strategy</span>
<small>The shipped contract for translation status.</small>
</a>

<a href="../../limitations/">
<strong>Read</strong>
<span>Limitations</span>
<small>Why translation rollout follows roadmap milestones.</small>
</a>

</div>
