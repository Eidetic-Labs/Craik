# Provider switching

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `craik provider` CLI surface — list, show, select. Output is
metadata-only and never contacts providers or loads secrets.

</div>

<div className="craik-keypoint">

**Selection is metadata, not authority.**

The CLI prints redacted payloads. It does not contact providers, load
secrets, or grant execution authority.

</div>

## Commands

<div className="craik-fields">

<div>
<dt>Command</dt>
<dt><span className="craik-fields__type">Output</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>craik provider list</code></dt>
<dt><span className="craik-fields__type">JSON metadata</span></dt>
<dd>Provider ids · supported modes · capabilities · trust boundaries · config references · secret reference names. <strong>Secret values are not printed.</strong></dd>
</div>

<div>
<dt><code>craik provider show &lt;id&gt;</code></dt>
<dt><span className="craik-fields__type">one record</span></dt>
<dd>Prints one provider by stable id.</dd>
</div>

<div>
<dt><code>craik provider select &lt;id&gt; --mode runner --policy-envelope-id &lt;id&gt;</code></dt>
<dt><span className="craik-fields__type">redacted payload</span></dt>
<dd>Selection payload. Unsupported modes are rejected before output.</dd>
</div>

</div>

## Selection payload

<div className="craik-grid">

<div><h4>Provider id</h4></div>
<div><h4>Provider family</h4></div>
<div><h4>Selected mode</h4></div>
<div><h4>Trust boundary</h4></div>
<div><h4>Runtime path</h4></div>
<div><h4>Config references</h4></div>
<div><h4>Secret reference names</h4></div>
<div><h4>Budget &amp; quota refs</h4></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Linked receipt ids</h4></div>

</div>

<div className="craik-keypoint">

**Compose with budgets and failover.**

Provider routing should check budget and quota status before
dispatch. Provider routing may fall back to another provider only
through an explicit failover policy that preserves policy envelope
boundaries and records the failover decision for audit.

</div>

## What's next

<div className="craik-next">

<a href="model-providers/">
<strong>Reference</strong>
<span>Model providers</span>
<small>The provider metadata catalog plus budget/quota gating.</small>
</a>

<a href="provider-failover/">
<strong>Reference</strong>
<span>Provider failover</span>
<small>The explicit fallback rules.</small>
</a>

<a href="../guides/provider-routing/">
<strong>Guide</strong>
<span>Provider routing &amp; sandboxes</span>
<small>End-to-end provider routing.</small>
</a>

</div>
