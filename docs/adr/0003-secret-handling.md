# 0003 Secret Handling

## Context

Craik writes receipts, handoffs, case files, provider configs, and local store
records. Those artifacts must be useful for audit and replay without leaking API
keys, tokens, local credentials, or copied secrets from adjacent tools.

## Decision

Craik stores and displays secret references, not secret values. Runtime configs
use environment-variable names or other non-secret references. Secrets are
resolved at request time by a resolver and are injected into transport headers by
a per-request header factory. Local persistence rejects unredacted secret-looking
payloads, and receipts redact request metadata before storage.

Errors and public docs must not include raw secret values. User-facing missing
secret errors should avoid disclosing unnecessary intent. Debug logging may name
references only when explicitly scoped for local diagnosis.

## Consequences

Operators can audit which credential reference was used without exposing the
credential. Provider transports and migration tools need explicit tests to prove
that authorization headers and copied secret values are not stored in exceptions,
receipts, docs, or fixtures.

## Alternatives Considered

Persisting encrypted secrets in Craik local state was rejected for the MVP
because it would make Craik a secret manager. Passing static headers into
transports was rejected because it would retain credentials on long-lived runtime
objects.

## Retraction

No retraction is active. Retract this ADR only if Craik formally adopts a secret
storage subsystem with rotation, encryption, access control, and audit semantics.
