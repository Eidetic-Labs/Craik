# Docker sandbox backend

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `DockerSandboxRequest` boundary that represents containerized
execution as an explicit environment decision — isolation defaults,
required refs, and the receipt path.

</div>

<div className="craik-keypoint">

**Does not start containers.**

The backend records and evaluates the decision. A separate governed
container runtime executes.

</div>

## What it records

`DockerSandboxRequest`:

<div className="craik-grid">

<div><h4>Backend id</h4></div>
<div><h4>Image reference</h4></div>
<div><h4>Command reference</h4></div>
<div><h4>Network mode</h4></div>
<div><h4>Mount references and target paths</h4></div>
<div><h4>Environment reference names</h4></div>
<div><h4>Privileged flag</h4></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Capability grant id</h4></div>
<div><h4>Receipt id</h4></div>

</div>

## Isolation defaults

Docker sandbox requests are **allowed only when**:

<ol className="craik-steps">
<li>Backend is <code>container</code> with <code>container</code> isolation.</li>
<li>Backend declares <code>container.run</code> with <code>run</code> operation.</li>
<li><code>privileged</code> is <code>false</code>.</li>
<li>Network mode is <code>none</code> or <code>restricted</code>.</li>
<li>Mounts are read-only by default.</li>
<li>Policy, grant, and receipt links are present.</li>
</ol>

<div className="craik-keypoint">

**Common denials.**

Requests using host-like network defaults, privileged containers,
read-write mounts, missing policy controls, or missing receipts are
denied before dispatch.

</div>

## Explicit settings

Image refs, command refs, mount refs, and environment refs are
references. They must not embed raw credentials, tokens, passwords, or
API keys.

## What's next

<div className="craik-next">

<a href="sandbox-backends/">
<strong>Reference</strong>
<span>Sandbox backends</span>
<small>The shared contract.</small>
</a>

<a href="environment-receipts/">
<strong>Reference</strong>
<span>Environment receipts</span>
<small>How allowed and denied decisions persist.</small>
</a>

<a href="local-process-backend/">
<strong>Reference</strong>
<span>Local process backend</span>
<small>The host-process alternative.</small>
</a>

</div>
