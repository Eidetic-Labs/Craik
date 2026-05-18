# Provider Routing And Sandboxes

Provider routing chooses model/runtime metadata. Sandbox routing chooses an
execution environment. Keep those decisions separate so policy, receipts, and
redaction can audit each boundary independently.

## Routing Flow

1. Select a model provider from [Model Providers](../reference/model-providers.md).
2. Check provider budget and quota before dispatch.
3. Evaluate [Provider Failover](../reference/provider-failover.md) only when a
   configured fallback rule allows it.
4. Use [MCP Client](../reference/mcp-client.md) metadata for provider or tool
   routes that cross an MCP boundary.
5. Select a [Sandbox Backend](../reference/sandbox-backends.md) for execution.
6. Record [Environment Receipts](../reference/environment-receipts.md) for
   allowed and denied provider or sandbox decisions.

## Provider Configuration

Provider records store non-secret metadata:

- provider id, family, modes, and capabilities;
- trust boundary;
- config reference names;
- secret reference names;
- budget and quota refs;
- runtime path;
- docs links.

Secret values do not belong in provider records, CLI output, docs, receipts, or
fixtures. Store raw provider credentials outside Craik and refer to them by
secret reference name.

## MCP Integration

Use [MCP Export Boundary](../reference/mcp-export-boundary.md) to decide which
Craik surfaces can be exported as MCP tools. Use
[MCP Client](../reference/mcp-client.md) for client-side provider and tool
routing.

MCP routes must remain:

- grant-required;
- receipt-required;
- redacted;
- documented when they are part of the compatibility surface.

## Sandbox Backends

The v0.9.0 sandbox surfaces are:

- [Local Process Backend](../reference/local-process-backend.md);
- [Remote Shell Backend](../reference/remote-shell-backend.md);
- [Browser Tool Boundary](../reference/browser-tool-boundary.md);
- [Docker Sandbox Backend](../reference/docker-sandbox-backend.md).

All sandbox actions require explicit policy, capability grants, receipts, and
redaction. Local and remote shell helpers use command references instead of
inline shell strings. Docker requests require explicit network, mount, image,
command, and environment references. Browser/tool results are redacted before
receipt metadata is persisted.

## Safe Diagnostics

List provider metadata:

```sh
craik provider list
```

Expected output is JSON metadata with provider ids, modes, capabilities, trust
boundaries, config refs, secret reference names, budget refs, quota refs, and
docs. Secret values are not printed.

Show one provider:

```sh
craik provider show provider_fixture_local
```

Expected output is one provider record. Missing provider ids return a clear CLI
error.

Select a provider for a mode:

```sh
craik provider select provider_fixture_local --mode runner --policy-envelope-id policy_provider
```

Expected output is a redacted selection payload with provider metadata, budget
and quota refs, policy envelope id, and receipt ids. The command does not call a
provider, load credentials, or grant execution authority.

Run local validation:

```sh
uv run --extra dev pytest tests/test_model_providers.py tests/test_mcp_client.py tests/test_sandbox_backend.py tests/test_environment_receipts.py
```

Expected output is passing tests for provider metadata, MCP client routing,
sandbox backend contracts, and environment receipts.

Run the aggregate sandbox policy boundary tests:

```sh
uv run --extra dev pytest tests/test_sandbox_policy_boundaries.py
```

Expected output is passing tests for allowed sandbox actions, denied missing
policy controls, denied unsafe isolation defaults, and redacted environment
receipts.

## Public Boundary

Do not include local filesystem paths, private hostnames, raw command payloads,
environment maps, webhook secrets, bearer tokens, SSH keys, provider
credentials, or unredacted tool outputs in public docs. Use stable fixture ids,
config refs, and secret reference names instead.
