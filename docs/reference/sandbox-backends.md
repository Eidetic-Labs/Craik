# Sandbox backends

<p className="craik-meta"><span>3 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `craik.sandbox_backend` contract — what it records, how isolation
modes pair with backend kinds, the policy boundary, and the
provider-neutrality rule.

</div>

<div className="craik-keypoint">

**Metadata-only.**

The contract does not execute commands, start containers, connect to
remote hosts, drive browsers, load secrets, or grant authority by
itself.

</div>

## What it records

<div className="craik-grid">

<div><h4>Stable backend id and name</h4></div>
<div><h4>Backend kind</h4><p><code>local_process</code> · <code>container</code> · <code>remote_shell</code> · <code>browser_tool</code>.</p></div>
<div><h4>Isolation mode</h4><p><code>process</code> · <code>container</code> · <code>remote</code> · <code>browser</code>.</p></div>
<div><h4>Capability names &amp; operations</h4></div>
<div><h4>Policy requirements</h4><p>Envelopes · grants · receipts · redaction.</p></div>
<div><h4>Non-secret runtime references</h4><p>And metadata.</p></div>
<div><h4>Documentation links</h4></div>

</div>

## Isolation modes

Backend kind and isolation mode must match.

| Backend kind | Isolation mode |
| --- | --- |
| `local_process` | `process` |
| `container` | `container` |
| `remote_shell` | `remote` |
| `browser_tool` | `browser` |

This keeps local, containerized, remote shell, and browser/tool
execution paths comparable while preserving their different trust
boundaries.

## Policy boundary

<div className="craik-keypoint">

**Every declared capability requires both a grant and a receipt.**

Sandbox backends require policy envelopes, capability grants,
receipts, and redaction.

</div>

## Provider neutrality

Sandbox backend records must not contain provider ids, model routing
choices, or secret-like metadata keys.

<div className="craik-decision">

<div>
<h4>Provider routing</h4>
<p>Chooses a model provider.</p>
</div>

<div>
<h4>Sandbox routing</h4>
<p>Chooses an execution backend.</p>
</div>

</div>

Those decisions stay separate so policy can audit each boundary
independently.

## Backend pages

<div className="craik-grid">

<div><h4><a href="../local-process-backend/">Local process backend</a></h4><p>Host process execution boundaries.</p></div>
<div><h4><a href="../remote-shell-backend/">Remote shell backend</a></h4><p>SSH and remote command boundaries.</p></div>
<div><h4><a href="../browser-tool-boundary/">Browser tool boundary</a></h4><p>Browser automation and tool execution boundaries.</p></div>
<div><h4><a href="../docker-sandbox-backend/">Docker sandbox backend</a></h4><p>Containerized execution boundaries.</p></div>

</div>

## What's next

<div className="craik-next">

<a href="../environment-receipts/">
<strong>Reference</strong>
<span>Environment receipts</span>
<small>What every sandbox decision records.</small>
</a>

<a href="../../guides/provider-routing/">
<strong>Guide</strong>
<span>Provider routing &amp; sandboxes</span>
<small>The end-to-end routing flow.</small>
</a>

<a href="../model-providers/">
<strong>Reference</strong>
<span>Model providers</span>
<small>The provider side of the dual-routing decision.</small>
</a>

</div>
