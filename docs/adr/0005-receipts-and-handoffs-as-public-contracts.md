# 0005 Receipts And Handoffs As Public Contracts

## Context

Craik's value depends on durable agent work: future agents and operators need to
know what happened, why it was allowed, what evidence was used, and what remains
unresolved. Receipts and handoffs therefore sit at the boundary between runtime
execution, memory, docs, and operator workflows.

## Decision

Capability receipts and handoffs are public Craik contracts. They are schema
validated, redacted before persistence, linked to policy envelopes where
available, and safe to cite from docs, operator views, work graphs, and recovery
flows. Receipts record capability decisions and outcomes; handoffs summarize run
state, completed actions, validation, risks, context debt, next steps, and
self-audit.

Incomplete or blocked runs should still produce handoffs when enough context is
available. Receipts and handoffs should link evidence by id rather than copying
private payloads.

## Consequences

The runtime can recover from interruptions and preserve accountability across
agent boundaries. The tradeoff is that new side-effect surfaces must emit or link
receipts instead of treating logs as sufficient evidence.

## Alternatives Considered

Plain text logs were rejected because they are difficult to validate, redact, and
query. Treating handoffs as optional prose was rejected because it breaks resume,
review, and cross-agent continuity.

## Retraction

No retraction is active. Retract this ADR if Craik replaces receipts and handoffs
with another versioned audit object and provides compatibility exports.
