# Stigmem compatibility

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The minimum Stigmem HTTP surface Craik v0.1.0 targets — endpoints,
error mapping, and capability detection.

</div>

<div className="craik-keypoint">

**Minimum compatibility, optional extensions.**

The required endpoints are baseline; optional endpoints unlock
ranked recall and contradiction import.

</div>

## Endpoints

| Endpoint | Required | Craik use |
| --- | --- | --- |
| `GET /healthz` | Yes | Reachability check. |
| `GET /.well-known/stigmem` | Yes | Capability and auth discovery. |
| `POST /v1/facts` | Yes | Direct fact writes when policy grants `memory.write`. |
| `GET /v1/facts` | Yes | Fact query and search fallback. |
| `GET /v1/facts/{fact_id}` | Yes | Load one fact by id. |
| `GET /v1/facts/{fact_id}/provenance` | Yes | Load fact provenance for evidence and case files. |
| `POST /v1/recall` | Optional | Future ranked recall path. |
| `GET /v1/conflicts` | Optional | Future contradiction import path. |

## Error mapping

| Stigmem response | Craik error |
| --- | --- |
| `401` | `StigmemAuthError` |
| `403` | `StigmemPermissionError` |
| Other HTTP failure | `StigmemRequestError` |
| Missing local config or incompatible response shape | `StigmemCapabilityError` |

## Capability detection

`craik connect stigmem` verifies the node can answer health, metadata,
and authenticated fact-query requests.

<div className="craik-grid">

<div><h4>Node URL</h4></div>
<div><h4>Node id</h4></div>
<div><h4>Whether auth is required</h4></div>
<div><h4>Required endpoint support</h4></div>
<div><h4>Optional recall / conflict / federation / source-attestation hints</h4></div>
<div><h4>Check timestamp</h4></div>

</div>

## What's next

<div className="craik-next">

<a href="../../guides/connecting-stigmem/">
<strong>Guide</strong>
<span>Connecting Stigmem</span>
<small>The operator-facing setup.</small>
</a>

<a href="../memory-backends/">
<strong>Reference</strong>
<span>Memory backends</span>
<small>The interface every backend implements.</small>
</a>

<a href="../../stigmem-integration/">
<strong>Read</strong>
<span>Stigmem integration</span>
<small>The full boundary, fact mapping, and contradiction strategy.</small>
</a>

</div>
