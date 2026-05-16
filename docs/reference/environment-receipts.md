# Environment Receipts

Environment receipts are normal `craik.capability_receipt` records for provider,
MCP, sandbox, local process, remote shell, browser, and container decisions.

`EnvironmentReceiptContext` links receipts to:

- task id;
- policy envelope id;
- provider id;
- sandbox backend id;
- route id;
- target id;
- command reference;
- prior receipt ids.

## Actions

Environment receipt actions are:

- `environment_decision`;
- `provider_action`;
- `sandbox_action`;
- `denial`.

Allowed actions use receipt status `passed`. Denied actions use receipt status
`denied` and preserve the denial reason.

## Redaction

Environment receipts redact environment variables, credentials, command
payloads, raw commands, stdin, stdout, stderr, target payloads, and secret-like
metadata keys such as tokens, API keys, passwords, and credentials.

Receipts should store command references and target references, not raw command
strings, environment maps, SSH material, provider tokens, or unredacted tool
payloads.

The builder in `craik.runtime.environment_receipts` does not execute actions or
grant authority. It builds auditable, redacted receipt records for callers that
have already made provider or sandbox routing decisions.
