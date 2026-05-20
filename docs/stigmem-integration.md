# Stigmem Integration

<p className="craik-meta"><span>9 min read</span><span>For integrators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

How Craik integrates with Stigmem as its reference memory and truth
substrate — the boundary, the memory-store interface, the minimum
compatibility target, endpoint mapping, capability detection, fact
mapping, source identity, the local proposal model, contradiction and
memory-diff strategies, error mapping, and the local backend.

</div>

<div className="craik-keypoint">

**Stigmem is the truth substrate. Craik is the runtime.**

Stigmem owns durable facts, provenance, scopes, trust, and conflict
detection. Craik owns case files, policy, capability grants, receipts,
handoffs, and the orchestration loop. The interface between them is a
small, versioned set of HTTP calls.

</div>

## Boundary

<div className="craik-decision">

<div>
<h4>Stigmem owns</h4>
<ul>
<li>Facts</li>
<li>Provenance</li>
<li>Scopes</li>
<li>Trust metadata</li>
<li>Contradiction tracking</li>
<li>Federation</li>
<li>Auth</li>
<li>Memory plugin hooks</li>
</ul>
</div>

<div>
<h4>Craik owns</h4>
<ul>
<li>Task orchestration</li>
<li>Project case files</li>
<li>Agent role assignment</li>
<li>Capability grants</li>
<li>Receipts</li>
<li>Handoffs</li>
<li>Work graph state</li>
<li>Operator workflows</li>
</ul>
</div>

</div>

## Memory-store interface

Craik defines a capability-based memory interface so non-Stigmem
backends remain feasible.

<div className="craik-grid">

<div>
<h4>Required base</h4>
<p>Read facts · propose facts · write facts · search facts · list by entity · attach provenance · record handoff references.</p>
</div>

<div>
<h4>Advanced</h4>
<p>Contradiction detection · trust tiers · scoped visibility · memory diff · expiration / stale-risk markers · federation.</p>
</div>

</div>

## Minimum compatibility target

The first Stigmem backend targets the current reference-node HTTP API.

<div className="craik-fields">

<div>
<dt>Required endpoints</dt>
<dt><span className="craik-fields__type">HTTP</span></dt>
<dd><code>GET /healthz</code> · <code>GET /.well-known/stigmem</code> · <code>POST /v1/facts</code> · <code>GET /v1/facts</code> · <code>GET /v1/facts/{`{fact_id}`}</code> · <code>GET /v1/facts/{`{fact_id}`}/provenance</code></dd>
</div>

<div>
<dt>Required auth</dt>
<dt><span className="craik-fields__type">behavior</span></dt>
<dd>Bearer API keys via <code>Authorization: Bearer &lt;key&gt;</code>. Detect requirement from <code>/.well-known/stigmem</code>. Surface <code>401</code>/<code>403</code> as configuration errors. Never log raw API keys.</dd>
</div>

<div>
<dt>Fact-model fields</dt>
<dt><span className="craik-fields__type">required</span></dt>
<dd><code>id</code> · <code>entity</code> · <code>relation</code> · <code>value</code> · <code>source</code> · <code>timestamp</code> · <code>confidence</code> · <code>scope</code></dd>
</div>

<div>
<dt>Assertion fields</dt>
<dt><span className="craik-fields__type">required</span></dt>
<dd><code>entity</code> · <code>relation</code> · <code>value</code> · <code>source</code> · <code>confidence</code> · <code>scope</code> · optional <code>valid_until</code> · optional <code>garden_id</code> · optional <code>attestation</code></dd>
</div>

<div>
<dt>Query filters</dt>
<dt><span className="craik-fields__type">required</span></dt>
<dd><code>entity</code> · <code>relation</code> · <code>source</code> · <code>scope</code> · <code>min_confidence</code> · <code>include_contradicted</code> · <code>include_expired</code> · <code>after</code> · <code>cursor</code> · <code>limit</code></dd>
</div>

<div>
<dt>Scopes</dt>
<dt><span className="craik-fields__type">required</span></dt>
<dd><code>local</code> · <code>team</code> · <code>company</code> · <code>public</code></dd>
</div>

</div>

<div className="craik-keypoint">

**Federation, gardens, source attestation, quarantine, tombstones,
vector recall, and plugins are not required.** Craik uses them when
the backend advertises them and falls back gracefully when it doesn't.

</div>

## Endpoint mapping

| Craik memory method | Stigmem endpoint | Required | Notes |
| --- | --- | --- | --- |
| `health()` | `GET /healthz` | Yes | Confirms node is reachable. |
| `discover()` | `GET /.well-known/stigmem` | Yes | Reads node id, URL, auth mode, federation, attestation, namespaces. |
| `write_fact(fact)` | `POST /v1/facts` | Yes | Used only when policy grants direct memory write. |
| `propose_fact(proposal)` | Local Craik store, optional later Stigmem fact | Yes | Stigmem has immutable facts, not a proposal queue; Craik keeps proposals locally until approved. |
| `search_facts(query, scope)` | Prefer `POST /v1/recall`; fallback to `GET /v1/facts` | Optional recall, required fallback | Recall gives ranked results; query is the minimum reliable path. |
| `list_facts(entity, relation, scope)` | `GET /v1/facts` | Yes | Paginate with `cursor` and `limit`. |
| `get_fact(fact_id)` | `GET /v1/facts/{fact_id}` | Yes | UUID or CID where node supports CID addressing. |
| `get_provenance(fact_id)` | `GET /v1/facts/{fact_id}/provenance` | Yes | Used to populate evidence and case files. |
| `list_contradictions()` | `GET /v1/conflicts` | Optional | Use if available; otherwise local contradiction reports. |
| `resolve_contradiction()` | `POST /v1/conflicts/{conflict_id}/resolve` | Optional | Requires explicit memory-write grant. |
| `memory_diff(run_id)` | Craik local store | Yes | Stigmem does not provide run-scoped diffs; Craik computes from proposals/writes. |

## Capability detection

At connect time, Craik probes the backend.

<ol className="craik-steps">
<li><code>GET /healthz</code> returns success.</li>
<li><code>GET /.well-known/stigmem</code> returns metadata.</li>
<li>If auth is required, authenticated <code>GET /v1/facts?limit=1</code> succeeds.</li>
<li>If writes are configured, Craik validates permissions by policy and surfaces the first write failure clearly (no dry-run available).</li>
</ol>

Optional probes — used when available, never required.

<div className="craik-grid">

<div><h4><code>POST /v1/recall</code></h4><p>Ranked retrieval.</p></div>
<div><h4><code>GET /v1/conflicts</code></h4><p>Stigmem-level contradictions.</p></div>
<div><h4><code>GET /v1/auth/keys</code></h4><p>Key inspection.</p></div>
<div><h4>Provenance endpoint</h4><p><code>GET /v1/facts/{`{fact_id}`}/provenance</code> availability.</p></div>
<div><h4>Source attestation</h4><p>Mode from well-known metadata.</p></div>
<div><h4>Federation</h4><p>Status from well-known metadata.</p></div>

</div>

Detected capabilities live in Craik local state and surface in case
files when relevant.

## Fact mapping

| Craik field | Stigmem field |
| --- | --- |
| `entity` | `entity` |
| `relation` | `relation` |
| `value` | `value` |
| `source` | `source` |
| `confidence` | `confidence` |
| `scope` | `scope` |
| `expires_at` | `valid_until` |
| `garden_id` | `garden_id` |
| `attestation` | `attestation` |

Craik uses stable relation namespaces and avoids the reserved
`stigmem:` prefix for ordinary product facts.

**Recommended prefixes:** `craik:task:*` · `craik:handoff:*` ·
`craik:receipt:*` · `craik:docs:*` · `craik:policy:*` · `codex:*` only
for Codex-specific automation or team-fact compatibility.

## Source and identity

<div className="craik-fields">

<div>
<dt>Source form</dt>
<dt><span className="craik-fields__type">When to use</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>agent:craik</code></dt>
<dt><span className="craik-fields__type">generic</span></dt>
<dd>Anonymous runtime source.</dd>
</div>

<div>
<dt><code>agent:craik:&lt;runner&gt;</code></dt>
<dt><span className="craik-fields__type">runner-scoped</span></dt>
<dd>Identifies the executing runner adapter.</dd>
</div>

<div>
<dt><code>agent:craik:&lt;runner&gt;:&lt;stable-agent-id&gt;</code></dt>
<dt><span className="craik-fields__type">identity-scoped</span></dt>
<dd>Identifies a stable agent identity within the runner.</dd>
</div>

<div>
<dt><code>user:&lt;id&gt;</code></dt>
<dt><span className="craik-fields__type">human</span></dt>
<dd>When the operator is the source of the assertion.</dd>
</div>

</div>

<div className="craik-keypoint">

**Attestation modes.**

If Stigmem source attestation runs in `enforce` mode, Craik either
sets `source` to the authenticated entity URI or attaches a valid
Stigmem agent-key attestation. In `warn` mode, Craik surfaces warnings
through receipts and handoffs.

</div>

## Local proposal model

Craik does not treat every proposed fact as an immediate Stigmem write.

<div className="craik-grid">

<div><h4>Agent-created facts</h4><p>Default to local memory proposals.</p></div>
<div><h4>Direct Stigmem writes</h4><p>Require an explicit memory-write grant.</p></div>
<div><h4>Approval flow</h4><p>User approval promotes proposals to Stigmem facts.</p></div>
<div><h4>Rejected proposals</h4><p>Stay local for audit unless retention policy removes them.</p></div>

</div>

This preserves Craik's strict-by-default posture while keeping Stigmem
as the durable truth substrate.

## Contradiction strategy

Stigmem exposes conflicts when facts with the same entity, relation,
and scope disagree. Craik uses Stigmem conflicts where the backend
provides them, but always keeps its own local contradiction reports.

<div className="craik-decision">

<div>
<h4>Stigmem conflicts</h4>
<p>When available, list with <code>GET /v1/conflicts?status=unresolved</code>. Link conflict facts into case files. Require explicit memory-write grant before <code>POST /v1/conflicts/{`{conflict_id}`}/resolve</code>.</p>
</div>

<div>
<h4>Local contradiction reports</h4>
<p>Not every Craik contradiction is a Stigmem-level conflict. Examples: docs say a task is planned but GitHub shows it merged · public docs contain internal-only labels · a handoff contradicts later branch state · a runner result conflicts with a verifier result.</p>
</div>

</div>

Local contradiction reports may later produce Stigmem fact proposals.

## Memory diff

Craik owns run-scoped memory diffs.

<div className="craik-grid">

<div><h4>Local proposals created</h4></div>
<div><h4>Proposals approved</h4></div>
<div><h4>Stigmem facts written</h4></div>
<div><h4>Stigmem write failures</h4></div>
<div><h4>Facts read into case file</h4></div>
<div><h4>Contradictions opened</h4></div>
<div><h4>Contradictions resolved</h4></div>
<div><h4>Handoff summary fact writes</h4></div>

</div>

Stigmem facts are referenced by `id` and `cid` when available.

## Error mapping

| HTTP status | Craik meaning |
| --- | --- |
| `400` | Invalid request or unsupported query shape. |
| `401` | Missing or invalid API key. |
| `403` | Insufficient Stigmem permission. |
| `404` | Missing fact, endpoint, or tombstone-hidden fact. |
| `409` | Duplicate or already-resolved lifecycle conflict. |
| `422` | Schema validation failure. |
| `5xx` | Node unavailable or internal node error. |

<div className="craik-keypoint">

**Error redaction is mandatory.**

Error messages must be redacted before they are persisted in receipts,
logs, handoffs, or case files.

</div>

## Stigmem fact usage

Craik uses Stigmem facts to assemble case files.

<div className="craik-grid">

<div><h4>Repo current state</h4></div>
<div><h4>Branch and PR status</h4></div>
<div><h4>Docs policy</h4></div>
<div><h4>ADR policy</h4></div>
<div><h4>Implementation decisions</h4></div>
<div><h4>Known gaps</h4></div>
<div><h4>Stale-risk docs</h4></div>
<div><h4>Agent handoffs</h4></div>
<div><h4>Capability constraints</h4></div>
<div><h4>Project conventions</h4></div>

</div>

## Stigmem fact writes

Craik writes facts when agents learn reusable project state.

<div className="craik-grid">

<div><h4>Doc policy</h4><p>That future agents must respect.</p></div>
<div><h4>Recurring validation command</h4></div>
<div><h4>Implementation constraint</h4></div>
<div><h4>Repository convention</h4></div>
<div><h4>Stale documentation warning</h4></div>
<div><h4>Completed migration status</h4></div>
<div><h4>Contradiction needing resolution</h4></div>

</div>

## Handoff storage

Handoffs live as structured artifacts; summary facts go to Stigmem.

The full handoff may live in Craik storage or the repository. Stigmem
receives enough metadata for discovery: task id · repository · branch ·
agent identity · summary · changed artifacts · facts learned ·
unresolved questions · handoff URI.

## Local development

<div className="craik-keypoint">

**Local memory is for dev and tests — not a product thesis.**

A local memory backend exists to lower setup friction and keep tests
deterministic. Stigmem remains the production-grade reference backend.

</div>

## What's next

<div className="craik-next">

<a href="../guides/connecting-stigmem/">
<strong>Guide</strong>
<span>Connecting Stigmem</span>
<small>Concrete connection steps, capability detection, and troubleshooting.</small>
</a>

<a href="../governance/">
<strong>Read</strong>
<span>Governance</span>
<small>How memory writes are policy-gated and receipt-backed.</small>
</a>

<a href="../runtime-contracts/">
<strong>Read</strong>
<span>Runtime contracts</span>
<small>The fact-proposal and memory-backend contract shapes.</small>
</a>

</div>
