# Receipts

Capability receipts are concise accountability records for important actions.

A receipt records:

- who acted,
- which task the action belonged to,
- which capability was used,
- what target was affected,
- why the action happened,
- which policy profile applied,
- whether the run was fail-open,
- and a redacted result summary.

Receipts are not full logs. They are durable records for actions that matter to governance, handoff continuity, and later review.

## Local Receipt Store

Craik persists `craik.capability_receipt` records in the local SQLite store.

The receipt store supports:

- recording validated receipts,
- loading one receipt by id,
- listing all receipts,
- filtering receipts by task id,
- filtering receipts by policy envelope id,
- and filtering receipts by handoff id.

Task linkage is a first-class receipt field. Policy envelope and handoff linkage are carried in receipt result metadata with these keys:

- `policy_envelope_id`
- `handoff_ids`

This keeps the v0.1.0 receipt contract stable while allowing the runtime to connect receipts to policy and handoff records.

## Redaction

Receipts must not contain raw secrets or credentials. Local persistence validates every stored receipt through the central redaction guard and rejects payloads that still appear to contain unredacted secret material.

Use redacted summaries and metadata instead of raw command output, request payloads, tokens, auth headers, or credential-bearing URLs.

## CLI

Use `craik receipts list` to inspect local receipts:

```sh
craik receipts list
craik receipts list --task-id task_docs_reconcile
craik receipts list --policy-id policy_docs_reconcile
craik receipts list --handoff-id handoff_docs_reconcile
```

Use `craik receipts show` to inspect one receipt:

```sh
craik receipts show receipt_pytest
```

Both commands print JSON payloads that match the `craik.capability_receipt` schema.

## Current Scope

The receipt store and query commands are implemented. Automatic receipt-producing wrappers for shell commands, file writes, GitHub writes, case files, and handoffs are planned runtime work.
