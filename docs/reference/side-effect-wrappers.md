# Side-Effect Wrappers

Craik side effects must pass through policy, grant, redaction, and receipt
boundaries. `craik.runtime.side_effects` provides MVP wrappers for:

- shell command references;
- repository file writes;
- durable memory or Stigmem fact writes;
- guarded GitHub write operations.

The wrappers persist denial receipts for blocked actions and passed environment
receipts for allowed actions. Shell and GitHub wrappers accept callbacks for the
actual execution boundary, which keeps tests deterministic and prevents ambient
side effects.

## Files

File writes use `check_file_write_grant` and `DocsProfile` immutable path rules.
Immutable paths require approval metadata and a matching
`repo.write.immutable` grant. Written content is redacted before persistence.

## Memory

Memory writes use `memory.write` grants and a durable writer interface. Public
metadata records entity, relation, scope, and confidence only; raw credentials or
secret material must not appear in receipts.

## GitHub

GitHub writes use `github.write` grants with explicit operations such as
`create_pr`. The wrapper records the operation and redacted result metadata.
