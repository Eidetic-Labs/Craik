# Human Delegation And Scope Changes

Human delegation points mark places where autonomous agents must stop or hand
off instead of continuing silently.

## Delegation Kinds

`craik.human_delegation_point` supports four kinds:

- `approval`: human authorization is required by policy or task boundary.
- `clarification`: the request is ambiguous enough that guessing would change
  behavior or scope.
- `escalation`: an unresolved risk, contradiction, or policy issue needs a
  human decision.
- `ownership_transfer`: the agent should transfer responsibility to a human or
  another owner before further work.

Open delegation points block autonomous continuation. Resolved delegation
points must include resolution text.

## Scope Changes

`craik.scope_change_request` records the current scope, proposed scope, reason,
intent lock, optional policy envelope, contradictions, and handoffs involved.
Pending requests also block autonomous continuation.

`craik.scope_change_result` records the human decision. Rejected changes keep
the existing scope. Accepted changes must link to an updated intent lock so the
new boundary is durable and auditable.

## Handoffs

Handoffs surface `open_human_delegation_ids`, `scope_change_request_ids`, and
`scope_change_result_ids`. A blocked handoff should list open delegation points
and explain what human input is required before work resumes.
