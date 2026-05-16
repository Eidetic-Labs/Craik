# Stigmem Compatibility

Craik v0.1.0 uses a minimum Stigmem compatibility surface.

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

## Error Mapping

| Stigmem response | Craik error |
| --- | --- |
| `401` | `StigmemAuthError` |
| `403` | `StigmemPermissionError` |
| Other HTTP failure | `StigmemRequestError` |
| Missing local config or incompatible response shape | `StigmemCapabilityError` |

## Capability Detection

`craik connect stigmem` verifies the node can answer health, metadata, and authenticated fact query requests. The resulting capability payload records:

- node URL,
- node id,
- whether auth is required,
- required endpoint support,
- optional recall/conflict/federation/source-attestation hints,
- and the check timestamp.
