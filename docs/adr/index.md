# Architecture decision records

<p className="craik-meta"><span>1 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

Durable design decisions, kept separately from mutable reference
material. Reference docs describe current behavior; ADRs explain why
the shape exists, what tradeoffs were accepted, and how the decision
can be retracted.

</div>

<div className="craik-keypoint">

**Each ADR is a contract.**

Status · Context · Decision · Consequences · Alternatives ·
Retraction. Retraction is the path to changing the design — not silent
drift.

</div>

## Records

<div className="craik-adr-grid">

<a className="craik-adr-card" href="../record-mvp-runner-scope/">
<span className="craik-adr-card__status">Accepted</span>
<span className="craik-adr-card__id">0001</span>
<strong>Record MVP runner scope</strong>
<span>The MVP runner path is a deterministic provider-backed certification path by default.</span>
</a>

<a className="craik-adr-card" href="../provider-transport-and-mode-families/">
<span className="craik-adr-card__status">Accepted</span>
<span className="craik-adr-card__id">0002</span>
<strong>Provider transport &amp; mode families</strong>
<span>Provider adapters and transports are separate. OpenAI Responses, Anthropic Messages, and Chat Completions are distinct families.</span>
</a>

<a className="craik-adr-card" href="../secret-handling/">
<span className="craik-adr-card__status">Accepted</span>
<span className="craik-adr-card__id">0003</span>
<strong>Secret handling</strong>
<span>Craik stores references, not secret values. Local persistence rejects unredacted payloads.</span>
</a>

<a className="craik-adr-card" href="../policy-envelope-shape/">
<span className="craik-adr-card__status">Accepted</span>
<span className="craik-adr-card__id">0004</span>
<strong>Policy envelope shape</strong>
<span>The stable governance boundary for any task-scoped action context. Capability grants are separate records.</span>
</a>

<a className="craik-adr-card" href="../receipts-and-handoffs-as-public-contracts/">
<span className="craik-adr-card__status">Accepted</span>
<span className="craik-adr-card__id">0005</span>
<strong>Receipts &amp; handoffs as public contracts</strong>
<span>Both are schema-validated, redacted, and safe to cite from docs, operator views, and recovery flows.</span>
</a>

<a className="craik-adr-card" href="../package-and-runtime-layout/">
<span className="craik-adr-card__status">Accepted</span>
<span className="craik-adr-card__id">0006</span>
<strong>Package &amp; runtime layout</strong>
<span>Runtime modules are grouped by concern under <code>runtime.*</code> packages. No package grows beyond 15 sibling modules.</span>
</a>

<a className="craik-adr-card" href="../credential-and-identity-architecture/">
<span className="craik-adr-card__status">Accepted</span>
<span className="craik-adr-card__id">0007</span>
<strong>Credential &amp; identity architecture</strong>
<span>Typed credential profiles · OIDC operator identity · workload identity and RFC 8693 token exchange · identity on every receipt.</span>
</a>

</div>

## What's next

<div className="craik-next">

<a href="../../runtime-contracts/">
<strong>Read</strong>
<span>Runtime contracts</span>
<small>The shipped contract surface ADRs 0004 / 0005 / 0007 stabilize.</small>
</a>

<a href="../../governance/">
<strong>Read</strong>
<span>Governance</span>
<small>How envelopes, grants, and operator/credential identity compose.</small>
</a>

<a href="../../architecture/">
<strong>Read</strong>
<span>Architecture</span>
<small>The seven runtime layers ADR 0006 organizes.</small>
</a>

</div>
