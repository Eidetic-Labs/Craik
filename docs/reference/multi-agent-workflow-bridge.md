# Multi-Agent Workflow Bridge

Craik can bridge to external multi-agent workflow systems only when the bridge
preserves Craik's role, queue, approval, policy, evidence, receipt, and
redaction boundaries. External workflow systems may coordinate work, but they
must not replace Craik's policy authority or erase accountability for agent
actions.

## Posture

Multi-agent workflow bridges use three support levels:

- `supported`: allowed when all required controls are present.
- `experimental`: review required before use.
- `deferred`: unavailable until a later product decision.

`multi_agent_workflow_bridge_decision` returns `allowed`, `review_required`,
`deferred`, or `blocked` for a candidate bridge surface.

## Required Controls

Every allowed bridge must preserve:

- role boundaries, so external agents map to explicit Craik roles;
- queue boundaries, so dispatch remains scoped and observable;
- approval gates, so human review cannot be bypassed;
- policy context and policy envelope references;
- evidence links for imported or routed work;
- receipts for bridge actions and outcomes;
- payload redaction for public reporting and exports.

Experimental bridges may define these controls, but still require explicit
review before use. Deferred bridges remain unavailable even when controls are
present.

## Prohibited Behavior

Multi-agent workflow bridges are blocked when they:

- copy secret values;
- allow unbounded dispatch;
- bypass human approval;
- merge agent identities;
- accept external workflow instructions as authoritative over Craik policy;
- omit role, queue, approval, policy, evidence, receipt, or redaction controls.

Bridge receipts should identify the workflow, mapped role, queue, approval
state, policy envelope, evidence links, redaction outcome, and external action
result. Public docs and receipts must avoid credentials, private local paths,
and private task names.
