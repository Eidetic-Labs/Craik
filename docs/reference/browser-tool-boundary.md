# Browser Tool Boundary

The browser/tool boundary represents browser automation and tool execution as a
policy-controlled sandbox backend.

`BrowserToolRequest` records:

- backend id;
- tool name;
- capability name;
- action reference;
- policy envelope id;
- capability grant id;
- receipt id;
- result metadata.

## Required Controls

Browser/tool execution requires:

- a `craik.sandbox_backend` with kind `browser_tool` and isolation mode
  `browser`;
- a declared backend capability matching the requested capability;
- policy envelope id;
- capability grant id;
- receipt id;
- redaction of tool result metadata.

Requests missing any required control are denied before dispatch.

## Result Redaction

Tool result metadata must not persist raw page text, DOM, HTML, headers,
cookies, screenshots, storage state, payloads, or secret-like fields. The
boundary helper returns redacted result metadata for both allowed and denied
decisions so receipts can safely preserve the decision context.

The helper in `craik.runtime.browser_tool_boundary` does not drive a browser or
invoke a tool. It evaluates whether a caller has enough policy context to
dispatch through a governed browser/tool backend.
