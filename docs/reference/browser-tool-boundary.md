# Browser tool boundary

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The policy-controlled boundary that represents browser automation and
tool execution as a sandbox backend — what the request records,
required controls, and redaction.

</div>

<div className="craik-keypoint">

**Evaluates dispatch, doesn't drive the browser.**

The helper in `craik.runtime.browser_tool_boundary` evaluates whether
a caller has enough policy context to dispatch through a governed
browser/tool backend. It does not drive a browser or invoke a tool.

</div>

## What it records

`BrowserToolRequest`:

<div className="craik-grid">

<div><h4>Backend id</h4></div>
<div><h4>Tool name</h4></div>
<div><h4>Capability name</h4></div>
<div><h4>Action reference</h4></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Capability grant id</h4></div>
<div><h4>Receipt id</h4></div>
<div><h4>Result metadata</h4></div>

</div>

## Required controls

<div className="craik-grid">

<div><h4>Sandbox backend</h4><p>Kind <code>browser_tool</code> · isolation <code>browser</code>.</p></div>
<div><h4>Declared backend capability</h4><p>Matching the requested capability.</p></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Capability grant id</h4></div>
<div><h4>Receipt id</h4></div>
<div><h4>Tool result metadata redaction</h4></div>

</div>

Requests missing any required control are denied before dispatch.

## Result redaction

<div className="craik-keypoint">

**No raw payloads in receipts.**

Tool result metadata must not persist raw page text, DOM, HTML,
headers, cookies, screenshots, storage state, payloads, or
secret-like fields. The boundary helper returns redacted metadata for
both allowed and denied decisions.

</div>

## What's next

<div className="craik-next">

<a href="../sandbox-backends/">
<strong>Reference</strong>
<span>Sandbox backends</span>
<small>The shared contract this boundary specializes.</small>
</a>

<a href="../environment-receipts/">
<strong>Reference</strong>
<span>Environment receipts</span>
<small>The receipt shape decisions produce.</small>
</a>

<a href="../../guides/provider-routing/">
<strong>Guide</strong>
<span>Provider routing &amp; sandboxes</span>
<small>End-to-end routing.</small>
</a>

</div>
