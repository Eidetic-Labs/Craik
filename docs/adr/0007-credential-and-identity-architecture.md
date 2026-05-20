# ADR 0007 · Credential and identity architecture

<p className="craik-meta"><span>4 min read</span><span>Accepted</span><span>Recorded 2026-05-09</span></p>

<div className="craik-lead">

**What this ADR decides**

That Craik treats credentials and operator identity as first-class
governance inputs. Typed `AuthProfile` records carry credential
identity, OIDC carries operator identity, and every provider receipt
binds both dimensions.

</div>

<div className="craik-keypoint">

**Governance thesis.**

Every action is authorized by a credential. Every credential is
authorized by an operator. Every authorization graph is itself
receipted.

</div>

## Context

Provider credentials and operator identity are governance inputs, not
incidental plumbing. Craik receipts need to answer which human
authorized work, which credential carried the provider call, which
policy allowed it, and which authorization grant made the credential
usable. Reconstructing those answers from environment variables or
local shell state would be fragile and would not survive handoffs,
audits, or future multi-agent coordination.

## Decision

### Credential identity

<div className="craik-grid">

<div><h4>Typed <code>AuthProfile</code></h4><p>Unit of credential identity. ID shape <code>&lt;provider_family&gt;:&lt;name&gt;</code>.</p></div>
<div><h4><code>CredentialSource</code> protocol</h4><p>Resolves request headers at call time.</p></div>
<div><h4>Env-var API keys</h4></div>
<div><h4>Local-CLI OAuth fallback</h4></div>
<div><h4>Vendor CLI bridge</h4></div>
<div><h4>External secret references</h4></div>
<div><h4>Stigmem-backed references</h4></div>
<div><h4>Marker identity</h4><p>For no-secret local providers.</p></div>

</div>

### Operator identity

<div className="craik-fields">

<div>
<dt>Mechanism</dt>
<dt><span className="craik-fields__type">Use case</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt>OIDC device-code flow</dt>
<dt><span className="craik-fields__type">headless / remote</span></dt>
<dd>Persistent operator session.</dd>
</div>

<div>
<dt>OIDC loopback + PKCE</dt>
<dt><span className="craik-fields__type">browser-capable entrypoints</span></dt>
<dd>Standard browser redirect.</dd>
</div>

<div>
<dt>Workload identity providers</dt>
<dt><span className="craik-fields__type">CI / cloud</span></dt>
<dd>No long-lived provider secrets.</dd>
</div>

<div>
<dt>RFC 8693 token exchange</dt>
<dt><span className="craik-fields__type">federation</span></dt>
<dd>Brokered credentials.</dd>
</div>

</div>

### Identity on every receipt

Provider receipts carry both dimensions:

<div className="craik-grid">

<div><h4><code>auth_profile_id</code></h4></div>
<div><h4><code>auth_kind</code></h4></div>
<div><h4><code>auth_identity_hash</code></h4></div>
<div><h4><code>operator_subject</code></h4></div>
<div><h4><code>operator_issuer</code></h4></div>
<div><h4><code>operator_email</code></h4></div>
<div><h4><code>operator_groups</code></h4></div>

</div>

### Policy constraints

Policy envelopes can constrain both dimensions:

<div className="craik-grid">

<div><h4><code>required_operator</code></h4></div>
<div><h4><code>allowed_operator_groups</code></h4></div>
<div><h4>Required issuer</h4></div>
<div><h4><code>allowed_credential_kinds</code></h4></div>
<div><h4><code>allowed_credential_profiles</code></h4></div>

</div>

<div className="craik-keypoint">

**Approval-gated first live use.**

First live use of a credential profile requires explicit operator
approval. Operator-to-profile authorization grants are stored on the
profile with a receipt chain so the authorization graph is queryable.

</div>

## Consequences

<div className="craik-grid">

<div><h4>Two-dimensional audit</h4><p>Every provider receipt records the operator who drove the work and the credential identity that carried it.</p></div>
<div><h4>Queryable identity</h4><p>Operators can query all actions taken by a human or all actions carried by a credential identity without exposing raw credentials.</p></div>
<div><h4>First-class authorization</h4><p>Credential authorization becomes durable state instead of tribal knowledge.</p></div>
<div><h4>Forward-compatible isolation</h4><p>Future multi-agent runtime can isolate credentials and operators per agent without redesigning receipts.</p></div>
<div><h4>Workload-identity ready</h4><p>CI and cloud deployments can use workload identity and token exchange instead of storing long-lived secrets.</p></div>
<div><h4>Tradeoff: setup surface</h4><p>Users need to understand operator login, credential profiles, approval, and policy constraints before using live providers in governed mode.</p></div>

</div>

## Alternatives considered

<div className="craik-fields">

<div>
<dt>Alternative</dt>
<dt><span className="craik-fields__type">Disposition</span></dt>
<dd>Why rejected</dd>
</div>

<div>
<dt>SAML for operator identity</dt>
<dt><span className="craik-fields__type">rejected for MVP</span></dt>
<dd>OIDC is more common for CLI, CI, and cloud-native auth flows.</dd>
</div>

<div>
<dt>Direct OIDC provider authentication</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>Major LLM providers do not currently accept arbitrary workload or operator OIDC tokens as provider credentials. Token exchange keeps the model extensible if providers add federation later.</dd>
</div>

<div>
<dt>Env-var-only credential resolution</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>Cannot represent Claude subscriber credentials, enterprise secret managers, team-shared Stigmem credentials, rotation, or per-profile authorization.</dd>
</div>

<div>
<dt>Static origin allowlists</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>Developer and CI environments often have dynamic origins, and origin checks do not answer which operator was authorized.</dd>
</div>

</div>

<div className="craik-keypoint">

**Retraction: none active.**

Retract this ADR if Craik adopts a federated identity mesh that makes
per-profile credential authorization and local operator sessions
obsolete.

</div>

## What's next

<div className="craik-next">

<a href="../../guides/authentication/">
<strong>Guide</strong>
<span>Authentication</span>
<small>The operator-facing setup flow this ADR backs.</small>
</a>

<a href="../secret-handling/">
<strong>ADR</strong>
<span>0003 · Secret handling</span>
<small>How credential values stay out of receipts and fixtures.</small>
</a>

<a href="../../governance/">
<strong>Read</strong>
<span>Governance</span>
<small>How operator and credential constraints compose with policy.</small>
</a>

</div>
