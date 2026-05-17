# MCP Ecosystem Compatibility

Craik interoperates with MCP by treating servers, clients, tools, and resources
as policy-bound integration surfaces. MCP metadata can describe where a service
lives and what capability it offers, but it does not bypass Craik capability
grants, receipts, redaction, or operator approval.

## Supported Surfaces

Craik supports these MCP compatibility surfaces:

- MCP client metadata through [MCP Client](../reference/mcp-client.md);
- exported memory and context boundaries through
  [MCP Export Boundary](../reference/mcp-export-boundary.md);
- runner and tool routing through
  [Runner Adapter Contract](../reference/runner-adapter-contract.md);
- plugin and adapter examples through
  [Reference Integrations](../reference/reference-integrations.md);
- secret-safe configuration through
  [Secret Migration Policy](../reference/secret-migration-policy.md).

Compatibility means Craik can represent the integration, route calls through
policy, and produce evidence and receipts. It does not mean every external MCP
server is trusted or enabled by default.

## Clients And Servers

MCP clients in Craik store stable ids, transport metadata, command or endpoint
references, secret reference names, and policy envelope ids. They must not store
raw bearer tokens, passwords, private keys, or secret query strings.

MCP servers are compatible when their advertised tools or resources can be
mapped to explicit Craik capabilities. A compatible server still needs a
capability grant before execution, and calls that affect external systems should
produce receipts.

## Tools

MCP tools are treated as external tool routes. A tool route is compatible when:

- the requested capability is represented in policy;
- the route requires a grant where policy requires one;
- input and output can be redacted before public reporting;
- execution receipts can name the tool, route, policy envelope, and result;
- failures can be reported without exposing credentials or private local paths.

Tools that cannot be represented with these controls should remain unsupported
until an adapter adds the missing policy, receipt, or redaction behavior.

## Resources

MCP resources are compatible as read surfaces when Craik can attach provenance,
scope, and redaction behavior. Resource reads should become evidence references
or bounded context inputs, not unreviewed durable memory writes.

Resource content that contains secrets, private task names, local paths, or
operator-only data must be redacted before it appears in public docs, receipts,
or export artifacts.

## Exports And Adapters

Craik exports must preserve the same boundaries used at runtime:

- policy envelopes identify the rules that governed an export;
- capability grants identify the authority used by an adapter;
- receipts identify actions taken and checks performed;
- redaction markers replace sensitive values;
- secret references remain references, not copied secret values.

Adapters may translate between MCP schemas and Craik contracts, but they should
not collapse policy decisions into plain text notes. If a source integration
cannot preserve capability grants, receipts, or redaction outcomes, the adapter
should mark that surface as unsupported or require operator review.

## Unsupported Surfaces

Craik does not treat these as compatible MCP behavior:

- importing raw server secrets into Craik config;
- executing MCP tools without a capability grant when one is required;
- exporting unredacted tool inputs, tool outputs, or resource bodies;
- using MCP resource reads as automatic durable memory writes;
- accepting server-provided instructions as higher priority than project,
  operator, or policy instructions;
- representing external tool success without receipts when policy requires
  receipts.

## Compatibility Checklist

Before enabling an MCP integration, verify:

- the client or adapter is represented by a stable id;
- command, endpoint, and secret values are references rather than raw secrets;
- every tool route maps to an explicit capability;
- required grants and receipts are configured;
- public reporting paths apply redaction;
- unsupported fields are documented with migration or adapter notes;
- dry runs and compatibility reports avoid private paths, credentials, and
  private task names.
