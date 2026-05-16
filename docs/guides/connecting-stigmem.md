# Connecting Stigmem

Craik can detect and use a Stigmem node through the minimum v0.1.0 HTTP endpoint surface.

Set the node URL and, when the node requires authentication, a bearer API key:

```sh
export CRAIK_STIGMEM_URL=http://127.0.0.1:18765
export CRAIK_STIGMEM_API_KEY=<api-key>
```

Check compatibility:

```sh
craik connect stigmem
```

The command calls:

- `GET /healthz`
- `GET /.well-known/stigmem`
- `GET /v1/facts?limit=1`

It prints a `craik.memory_backend_capabilities` payload and never prints the API key.

## Direct Writes

Craik still defaults to memory proposals. Direct Stigmem fact writes require a matching `memory.write` policy grant and use `POST /v1/facts`.

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

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `CRAIK_STIGMEM_URL` | Base URL for the Stigmem node. |
| `CRAIK_STIGMEM_API_KEY` | Bearer token for authenticated nodes. |
| `CRAIK_STIGMEM_TIMEOUT` | Request timeout in seconds. Defaults to `5.0`. |

Store API keys in the environment or local secret tooling. Do not commit them to project files.
