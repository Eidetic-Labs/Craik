# Locale i18n framework

<p className="craik-meta"><span>3 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

How locale preferences, translatable documents, and resolution work
together to keep runtime identifiers stable while operator-facing
text follows locale chains and fallbacks.

</div>

<div className="craik-keypoint">

**Runtime ids stay language-neutral.**

Translation may change operator-facing prose, but schema names, ids,
receipt ids, policy envelope ids, evidence ids, memory entities, and
task ids remain language-neutral.

</div>

## Locale preferences

`LocalePreference` records:

<div className="craik-grid">

<div><h4>Preferred locale</h4></div>
<div><h4>Fallback locales</h4></div>
<div><h4>Default locale</h4></div>
<div><h4>Fallback strategy</h4></div>
<div><h4>Optional formatting locale</h4></div>

</div>

### Fallback strategies

<div className="craik-fields">

<div>
<dt>Strategy</dt>
<dt><span className="craik-fields__type">Resolution order</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>exact_then_language</code></dt>
<dt><span className="craik-fields__type">full → language → fallbacks → default</span></dt>
<dd>Try the full locale, then the language subtag, then configured fallbacks and default.</dd>
</div>

<div>
<dt><code>exact_then_default</code></dt>
<dt><span className="craik-fields__type">full → fallbacks → default</span></dt>
<dd>Skip language-subtag step.</dd>
</div>

<div>
<dt><code>default_only</code></dt>
<dt><span className="craik-fields__type">full → default</span></dt>
<dd>Skip user fallbacks entirely.</dd>
</div>

</div>

## Translatable docs

`TranslatableDocMetadata` records a stable language-neutral id, source
path, source locale, available locales, translated paths, policy
envelope, evidence, receipts, and redaction requirements.

## Resolution

`resolve_doc_locale` returns a `LocaleResolution` with:

<div className="craik-grid">

<div><h4>Requested locale</h4></div>
<div><h4>Resolved locale</h4></div>
<div><h4>Status</h4><p><code>source</code> · <code>translated</code> · <code>fallback</code> · <code>missing</code>.</p></div>
<div><h4>Resolved path</h4></div>
<div><h4>Fallback chain</h4></div>
<div><h4>Policy · evidence · receipt · redaction metadata</h4></div>

</div>

<div className="craik-keypoint">

**Always public-safe.**

When a translation is unavailable, Craik falls back to the configured
chain and ultimately the source document. Public docs and translated
exports must continue to avoid credentials, private local paths, and
private task names.

</div>

## Boundaries

Locale support preserves:

<div className="craik-grid">

<div><h4>Policy decisions</h4><p>And envelope references.</p></div>
<div><h4>Evidence &amp; receipt links</h4></div>
<div><h4>Redaction markers</h4><p>And secret references.</p></div>
<div><h4>Stable runtime identifiers</h4></div>
<div><h4>Formatting boundaries</h4><p>For dates, numbers, locale-specific display text.</p></div>

</div>

Translation review receipts record the source document, translated
locale, reviewer or automation evidence, and confirmation that policy
and redaction semantics were preserved.

## What's next

<div className="craik-next">

<a href="../../guides/translated-docs/">
<strong>Guide</strong>
<span>Translated documentation strategy</span>
<small>The author-facing rules.</small>
</a>

<a href="../schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>Where translatable-doc metadata sits in the contract catalog.</small>
</a>

<a href="../public-boundary-provenance/">
<strong>Reference</strong>
<span>Public boundary</span>
<small>What translated docs must not expose.</small>
</a>

</div>
