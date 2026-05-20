# ADR 0003 · Secret handling

<p className="craik-meta"><span>2 min read</span><span>Accepted</span><span>Recorded 2026-05-01</span></p>

<div className="craik-lead">

**What this ADR decides**

That Craik stores and displays secret references, not secret values.
Secrets are resolved at request time and injected into transport
headers by a per-request header factory. Local persistence rejects
unredacted secret-looking payloads.

</div>

<div className="craik-keypoint">

**Status: Accepted.**

The product premise is durable, auditable agent work. That value
breaks immediately if receipts, handoffs, or fixtures leak credentials.

</div>

## Context

Craik writes receipts, handoffs, case files, provider configs, and
local store records. Those artifacts must be useful for audit and
replay without leaking API keys, tokens, local credentials, or copied
secrets from adjacent tools.

## Decision

<div className="craik-grid">

<div><h4>References, not values</h4><p>Runtime configs use env-var names or other non-secret references.</p></div>
<div><h4>Request-time resolution</h4><p>A resolver injects secrets into transport headers via a per-request header factory.</p></div>
<div><h4>Persistence rejection</h4><p>Local persistence rejects unredacted secret-looking payloads.</p></div>
<div><h4>Receipt redaction</h4><p>Receipts redact request metadata before storage.</p></div>
<div><h4>Public surfaces</h4><p>Errors and public docs must not include raw secret values. Missing-secret errors avoid disclosing unnecessary intent.</p></div>
<div><h4>Debug logging</h4><p>May name references only when explicitly scoped for local diagnosis.</p></div>

</div>

## Consequences

Operators can audit which credential reference was used without
exposing the credential. Provider transports and migration tools need
explicit tests to prove that authorization headers and copied secret
values are not stored in exceptions, receipts, docs, or fixtures.

## Alternatives considered

<div className="craik-fields">

<div>
<dt>Alternative</dt>
<dt><span className="craik-fields__type">Disposition</span></dt>
<dd>Why rejected</dd>
</div>

<div>
<dt>Persist encrypted secrets in local state</dt>
<dt><span className="craik-fields__type">rejected for MVP</span></dt>
<dd>Would turn Craik into a secret manager — out of scope for the runtime.</dd>
</div>

<div>
<dt>Static headers into transports</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>Would retain credentials on long-lived runtime objects.</dd>
</div>

</div>

<div className="craik-keypoint">

**Retraction: none active.**

Retract this ADR only if Craik formally adopts a secret-storage
subsystem with rotation, encryption, access control, and audit
semantics.

</div>

## What's next

<div className="craik-next">

<a href="../credential-and-identity-architecture/">
<strong>ADR</strong>
<span>0007 · Credential and identity architecture</span>
<small>How references compose with typed profiles and operator identity.</small>
</a>

<a href="../../reference/redaction/">
<strong>Reference</strong>
<span>Redaction</span>
<small>How redaction is applied across receipts, handoffs, and docs.</small>
</a>

<a href="../../security/secrets/">
<strong>Security</strong>
<span>Secrets handling</span>
<small>The operator-facing secrets guide.</small>
</a>

</div>
