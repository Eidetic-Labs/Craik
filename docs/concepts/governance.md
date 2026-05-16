# Governance

Craik governance is strict by default. Agents should know what they can read,
what they can change, which actions need approval, and which actions must leave
receipts.

The v0.1.0 governance surface includes:

- policy profiles,
- capability grant checks,
- immutable path protection,
- fail-open visibility,
- receipt requirements,
- redaction requirements,
- memory proposal defaults,
- and policy regression tests.

## Strict Defaults

`strict` is the default policy profile. It allows read-oriented context assembly
and receipt writing, but denies writes, shell execution, GitHub writes, and
direct memory writes unless a matching grant exists.

## Fail-Open

`trusted-local` can fail open only when explicitly requested. Fail-open use must
be visible in the policy envelope and receipt trail. Fail-open does not bypass
immutable path protection, redaction, receipts, or direct memory-write approval.

## Automation

`automation` is fail-closed. It is intended for CI and unattended workflows where
the safe behavior is to stop rather than widen authority.

## Release Gate

`craik policy test` checks the core governance invariants:

- immutable path protection,
- proposal-first memory writes,
- trusted-local fail-open receipts,
- automation fail-closed behavior,
- runner grant boundary tracking,
- and redaction for policy-relevant payload shapes.

See [Policy Profiles](../reference/policy-profiles.md),
[Capability Grants](../guides/capability-grants.md), and
[Policy Tests](../reference/policy-tests.md).
