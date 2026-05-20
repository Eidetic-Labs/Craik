# Redaction

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The central runtime redaction utility — primary APIs, default
coverage, structured-payload behavior, custom patterns, and the
persistence boundary every payload must cross redacted.

</div>

<div className="craik-keypoint">

**Redaction failures are security bugs.**

The local SQLite store rejects payloads that still appear to contain
unredacted secret material.

</div>

## Module

```text
craik.runtime.policy.redaction
```

The legacy `craik.runtime.redaction` import remains available for
compatibility.

## Primary APIs

<div className="craik-fields">

<div>
<dt>API</dt>
<dt><span className="craik-fields__type">Returns</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>redact(value, config=None)</code></dt>
<dt><span className="craik-fields__type">redacted value</span></dt>
<dd>Recursively redacts a value using the default or provided config.</dd>
</div>

<div>
<dt><code>contains_unredacted_secret(value, config=None)</code></dt>
<dt><span className="craik-fields__type">bool</span></dt>
<dd>Boundary check used by persistence to refuse unsafe payloads.</dd>
</div>

</div>

## Default coverage

<div className="craik-grid">

<div><h4>Bearer tokens</h4></div>
<div><h4>API key · token · password · secret assignments</h4></div>
<div><h4>Common token prefixes</h4></div>
<div><h4>Auth URLs</h4><p>With embedded credentials.</p></div>
<div><h4>Structured keys</h4><p>Containing secret-like names.</p></div>

</div>

## Structured payloads

Redaction applies recursively to dictionaries, lists, tuples, and
strings — and preserves non-secret shape. Object keys, status fields,
request ids, and non-secret summaries remain intact so debugging
context survives.

## Configurable patterns

Callers may provide custom regex patterns through `RedactionConfig`.
Custom patterns are additive when the caller includes the default
patterns plus project-specific patterns in the config.

## Persistence boundaries

Payloads must be redacted before they are written to:

<div className="craik-grid">

<div><h4>Logs</h4></div>
<div><h4>Receipts</h4></div>
<div><h4>Handoffs</h4></div>
<div><h4>Case files</h4></div>
<div><h4>Errors</h4></div>
<div><h4>Memory proposals</h4></div>
<div><h4>Work graph events</h4></div>

</div>

## What's next

<div className="craik-next">

<a href="../../adr/secret-handling/">
<strong>ADR</strong>
<span>0003 · Secret handling</span>
<small>The design behind references-not-values.</small>
</a>

<a href="../../security/secrets/">
<strong>Security</strong>
<span>Secrets handling</span>
<small>Operator-facing secrets guide.</small>
</a>

<a href="../policy-profiles/">
<strong>Reference</strong>
<span>Policy profiles</span>
<small>Profiles that mark redaction as required.</small>
</a>

</div>
