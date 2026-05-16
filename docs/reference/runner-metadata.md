# Runner Metadata

Runner metadata is captured at adapter boundaries so receipts and handoffs can
explain which runner produced work without adding provider-specific fields to
the stable contract surface.

## Stable Metadata

Craik records these stable keys for adapter-produced work:

- `runner_id`
- `runner_name`
- `adapter`
- `adapter_version`
- `execution_mode`
- `capabilities`
- `trust_profile`
- `capability_profile`
- `policy_notes`

Receipts store this snapshot under
`craik.capability_receipt.result.metadata.runner_metadata`. Handoffs preserve
the first unique runner snapshots they find on task receipts in
`craik.handoff.runner_metadata`.

## Runner-Specific Metadata

Runner-specific details remain nested under `runner_specific`. This is where
preview adapters can preserve local fixture mode, live availability, executable
names, or provider-specific session metadata without promoting those fields to
the core contract.

All runner metadata snapshots are redacted before they are stored or copied into
handoffs. Secret-like keys such as tokens, passwords, API keys, and credentials
are replaced with `[REDACTED]`.

## Boundaries

Receipt and handoff metadata is descriptive. It does not grant tool authority,
prove that external execution occurred, or replace policy receipts for concrete
side effects. Capability grants and policy checks remain the source of authority.
