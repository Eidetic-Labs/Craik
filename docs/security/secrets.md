# Secrets

Design rationale: [ADR 0003 Secret Handling](../adr/0003-secret-handling.md).

Craik treats secrets as sensitive runtime data.

Defaults:

- Local secrets belong under `~/.craik/secrets/`, or under `$CRAIK_HOME/secrets/` when `CRAIK_HOME` is set.
- Secrets paths are created with owner-only permissions where supported.
- Secrets should not be written to project-local `.craik/` directories.
- Receipts, logs, case files, handoffs, and memory proposals should use redacted summaries instead of raw secret values.

Issue #3 only creates the local state locations. It does not store credentials or add runtime authority to read or write secrets.

Policy profiles do not bypass redaction. The trusted-local fail-open profile still requires redacted receipts and must not persist raw secret values.

Capability grants do not authorize unredacted secret persistence. Secret handling remains governed by redaction rules even when an action is otherwise allowed.

The central redaction utility lives in `craik.runtime.policy.redaction`. It
redacts bearer tokens, common key/value secret shapes, auth URLs, configured
secret patterns, and structured fields with secret-like names before
persistence. The legacy `craik.runtime.redaction` import remains available for
compatibility.
