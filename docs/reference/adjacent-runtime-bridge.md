# Adjacent Runtime Bridge

Craik can bridge to adjacent runtimes only when the bridge preserves Craik's
policy, evidence, capability grant, receipt, and redaction boundaries. A bridge
may route work to another runtime, but it must not turn that runtime into a
source of higher-priority instructions or unbounded tool authority.

## Posture

Adjacent runtime bridges use three support levels:

- `supported`: allowed when all required controls are present.
- `experimental`: review required before use.
- `deferred`: unavailable until a later product decision.

`adjacent_runtime_bridge_decision` returns `allowed`, `review_required`,
`deferred`, or `blocked` for a candidate bridge surface.

## Required Controls

Every allowed adjacent runtime bridge must provide:

- a policy envelope id;
- preserved policy context;
- preserved evidence links;
- explicit capability grants;
- execution receipts;
- input and output redaction;
- a documented decision when exposed as a supported integration.

Experimental bridges may define these controls, but still require explicit
review before use. Deferred bridges remain unavailable even when the controls
are present.

## Prohibited Behavior

Adjacent runtime bridges are blocked when they:

- copy secret values;
- grant unbounded tool access;
- accept adjacent runtime instructions as authoritative over Craik policy;
- mutate external or local state without operator approval;
- omit policy envelope context;
- omit capability grants, receipts, evidence, or redaction controls.

Bridge receipts should identify the runtime, route, policy envelope, evidence
links, capability grant, redaction outcome, and operator approval when a
mutation is requested.
