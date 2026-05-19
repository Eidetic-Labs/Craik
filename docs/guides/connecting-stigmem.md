# Connecting Stigmem

<p className="craik-meta"><span>3 min read</span><span>For operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Point Craik at a Stigmem node, check compatibility, and learn the
default posture for memory writes (proposals first, direct writes only
under explicit grant).

</div>

<div className="craik-keypoint">

**Compatibility is detected, not assumed.**

`craik connect stigmem` probes the minimum v0.1.0 endpoints and prints
a backend-capabilities payload. The API key is never printed.

</div>

## Configure the node

Set the node URL and, when the node requires authentication, a bearer
API key.

```sh
export CRAIK_STIGMEM_URL=http://127.0.0.1:18765
export CRAIK_STIGMEM_API_KEY=<api-key>
```

## Check compatibility

```sh
craik connect stigmem
```

The command probes the minimum endpoints:

<div className="craik-grid">

<div><h4><code>GET /healthz</code></h4></div>
<div><h4><code>GET /.well-known/stigmem</code></h4></div>
<div><h4><code>GET /v1/facts?limit=1</code></h4></div>

</div>

It prints a `craik.memory_backend_capabilities` payload and never
prints the API key.

## Direct writes

<div className="craik-keypoint">

**Proposals are the default.**

Direct Stigmem fact writes require a matching <code>memory.write</code>
policy grant and use <code>POST /v1/facts</code>. Without a grant,
agent-created facts become local proposals.

</div>

Use local proposals when a task does not have direct write authority:

```sh
craik memory propose task_review_docs \
  --entity repo:example \
  --relation craik:current_state \
  --value "Documentation reconciliation requires evidence." \
  --source docs/guides/connecting-stigmem.md \
  --evidence-source docs/guides/connecting-stigmem.md \
  --evidence-locator docs/guides/connecting-stigmem.md \
  --evidence-summary "The connection guide documents Stigmem compatibility."
```

## Environment variables

<div className="craik-fields">

<div>
<dt>Variable</dt>
<dt><span className="craik-fields__type">Default</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>CRAIK_STIGMEM_URL</code></dt>
<dt><span className="craik-fields__type">unset</span></dt>
<dd>Base URL for the Stigmem node.</dd>
</div>

<div>
<dt><code>CRAIK_STIGMEM_API_KEY</code></dt>
<dt><span className="craik-fields__type">unset</span></dt>
<dd>Bearer token for authenticated nodes.</dd>
</div>

<div>
<dt><code>CRAIK_STIGMEM_TIMEOUT</code></dt>
<dt><span className="craik-fields__type"><code>5.0</code></span></dt>
<dd>Request timeout in seconds.</dd>
</div>

</div>

Store API keys in the environment or local secret tooling — never
commit them to project files.

## Stigmem-backed credentials

Craik can also resolve provider credentials from Stigmem facts through
`stigmem-ref` auth profiles. The profile points at a Stigmem node,
entity, scope, and relation such as `craik:credential:value`;
credential material is resolved at request time and is not printed in
receipts or logs.

This is useful when a team wants shared provider credentials with
Stigmem provenance and revocation semantics. The auth profile metadata
is file-backed in `<CRAIK_HOME>/auth-profiles.json`.

## What's next

<div className="craik-next">

<a href="../memory-proposals/">
<strong>Guide</strong>
<span>Memory proposals</span>
<small>The default unprivileged path for agent-created facts.</small>
</a>

<a href="../authentication/">
<strong>Guide</strong>
<span>Authentication</span>
<small>Profile shape and audit behavior for <code>stigmem-ref</code> credentials.</small>
</a>

<a href="../../stigmem-integration/">
<strong>Read</strong>
<span>Stigmem integration</span>
<small>The full boundary, endpoints, and fact-mapping reference.</small>
</a>

</div>
