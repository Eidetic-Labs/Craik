# MCP Client

Craik MCP client configuration is metadata for provider and tool routing. It is
not a secret store and does not grant runtime authority by itself.

`craik.runtime.mcp_client.MCPClientConfig` records:

- stable client id and name;
- transport: `stdio`, `http`, or `sse`;
- non-secret server, endpoint, command, and config references;
- secret reference names for external secret tooling;
- policy envelope id when the client is bound to a policy;
- grant, receipt, and redaction requirements;
- docs and non-secret metadata.

HTTP and SSE clients require an `endpoint_ref`. Stdio clients require a
`command_ref`. These fields are references or configured names; they should not
embed raw credentials, bearer tokens, API keys, passwords, or secret query
values.

## Routes

`MCPClientRoute` links a client to either a provider route or a tool route. A
route records:

- route id;
- client id;
- route kind: `provider` or `tool`;
- target reference, such as a provider id or tool name;
- required capability;
- whether the route requires a grant and receipt.

Routes are compatible only when they belong to the selected client and remain
grant- and receipt-required.

## Audit Boundary

MCP calls should be receipt-ready before dispatch. Compatibility checks return
the route ids, required controls, and reasons for blocked routes so callers can
write audit records through the normal receipt workflow.

MCP client metadata must stay redacted. Store raw endpoint secrets, bearer
tokens, and credentials outside Craik configuration and refer to them by
`secret_ref_names`.
