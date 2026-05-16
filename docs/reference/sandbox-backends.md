# Sandbox Backends

`craik.sandbox_backend` describes an execution environment backend without
binding it to any model provider.

The contract records:

- stable backend id and name;
- backend kind: `local_process`, `container`, `remote_shell`, or
  `browser_tool`;
- isolation mode: `process`, `container`, `remote`, or `browser`;
- capability names and operations exposed by the backend;
- policy requirements for envelopes, grants, receipts, and redaction;
- non-secret runtime references and metadata;
- documentation links.

## Isolation Modes

Backend kind and isolation mode must match:

| Backend kind | Isolation mode |
| --- | --- |
| `local_process` | `process` |
| `container` | `container` |
| `remote_shell` | `remote` |
| `browser_tool` | `browser` |

This keeps local, containerized, remote shell, and browser/tool execution paths
comparable while preserving their different trust boundaries.

## Policy Boundary

Sandbox backends require policy envelopes, capability grants, receipts, and
redaction. Each declared capability must require both a grant and a receipt.

The contract is metadata-only. It does not execute commands, start containers,
connect to remote hosts, drive browsers, load secrets, or grant authority by
itself.

## Provider Neutrality

Sandbox backend records must not contain provider ids, model routing choices, or
secret-like metadata keys. Provider routing can choose a model provider, and
sandbox routing can choose an execution backend, but those decisions stay
separate so policy can audit each boundary independently.

For host process execution boundaries, see
[Local Process Backend](local-process-backend.md).

For SSH and remote command boundaries, see
[Remote Shell Backend](remote-shell-backend.md).

For browser automation and tool execution boundaries, see
[Browser Tool Boundary](browser-tool-boundary.md).

For containerized execution boundaries, see
[Docker Sandbox Backend](docker-sandbox-backend.md).
