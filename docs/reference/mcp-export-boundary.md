# MCP Export Boundary

Craik can expose an MCP server surface only when the exported tools preserve the
same policy boundaries used by local runner, gateway, and plugin workflows.

The current decision is conservative: stable, documented metadata and workflow
surfaces can be exported; unstable internal surfaces, raw store internals, and
secret-bearing operations are not exportable.

## Export Criteria

An MCP surface is exportable when it:

- has a stable contract and documented compatibility expectations;
- does not expose raw secrets, tokens, credentials, signatures, or unredacted
  payloads;
- does not expose internal storage layouts, private state machines, or unstable
  implementation details;
- uses explicit capability grants for capability-bearing tools;
- records receipts for side-effect capabilities such as file writes, shell
  execution, network access, memory writes, and review comments;
- returns redacted metadata rather than ambient runtime authority.

Experimental surfaces require compatibility review before export. Internal
surfaces are blocked until promoted to a stable contract.

## Chosen Boundary

Craik MCP exports should be contract-first. Exported tools should wrap stable
runtime contracts and documented command behavior, not private Python objects or
database tables.

Allowed examples:

- read-only project, case file, handoff, receipt, and work graph inspection;
- provider selection metadata that omits secret values;
- policy preview and validation results;
- documented runner or gateway status summaries.

Blocked examples:

- raw secret reads or secret file browsing;
- direct local store table access;
- write, shell, network, memory-write, or review-comment tools without matching
  capability grants and receipts;
- experimental sandbox or provider internals without compatibility review.

## Compatibility Expectations

MCP tool names, input shapes, output fields, and error reasons are compatibility
surface. Changes should be additive where possible. Removing a field, changing a
status value, or exposing a previously redacted field requires review and
documentation updates.

Callers should treat `review_required` decisions as non-exportable until a human
or release process promotes the surface. `blocked` decisions require a boundary
change before export.

The `craik.runtime.mcp_export` helper records the decision status, reason, and
required controls for a candidate surface. It does not start an MCP server or
grant runtime authority by itself.

For client-side provider and tool routing, see [MCP Client](mcp-client.md).
