# 0004 Policy Envelope Shape

## Context

Craik coordinates agent work across file changes, shell commands, provider calls,
memory writes, handoffs, channel ingress, and sandbox backends. Each action needs
a stable record of actor, task, profile, grant requirements, redaction posture,
and receipt obligations.

## Decision

`craik.policy_envelope` is the stable governance boundary for a task-scoped
action context. It records the policy profile, actor, task id, allowed
capabilities, fail-open posture, receipt requirements, handoff requirements, and
redaction requirements. Capability grants are separate records so approvals can
be linked, expired, denied, or carried into receipts independently.

Provider loops, side-effect wrappers, channels, sandboxes, and memory workflows
must check the policy envelope and grants before executing side effects.

## Consequences

Policy behavior is explicit in artifacts rather than implicit in code paths.
This makes receipts and handoffs auditable, but it requires every new surface to
thread policy envelope ids and grant ids through its contracts.

## Alternatives Considered

Embedding policy decisions directly in task records was rejected because policy
can vary by actor and action. Relying only on runtime exceptions was rejected
because it would not produce durable evidence for reviewers or future agents.

## Retraction

No retraction is active. Retract this ADR if Craik replaces policy envelopes with
a formally versioned external authorization service and migration path.
