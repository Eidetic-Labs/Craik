# Multi-Agent Workflow Migration Assessment

Multi-agent workflow migration assessments describe how external workflow
systems map into Craik before bridges or importers are built.

`MultiAgentWorkflowMapping` records:

- source concept;
- target workflow concept: `agent`, `role`, `queue`, `artifact`, `memory`, or
  `approval`;
- target Craik surface;
- support level: `supported`, `partial`, or `unsupported`;
- notes;
- required controls;
- unsupported fields.

`MultiAgentWorkflowMigrationAssessment` records:

- assessment id;
- workflow name;
- overall support level;
- mappings;
- policy notes;
- redaction requirement;
- policy envelope id;
- evidence ids;
- receipt ids.

## Compatibility

Agents and roles can map to Craik agent roles when authority is explicit.
Queues can map to delegation queues only when dispatch, ownership, receipts, and
operator review are bounded. Artifacts, memories, and approvals must preserve
evidence, receipt, policy, and redaction semantics.

Unbounded autonomous queues, hidden side effects, raw private artifacts, and
approval steps without receipts are unsupported.

## Boundary

An assessment is not a bridge. It records migration compatibility and risks so
later dry runs, migration maps, and bridge decisions can stay reviewable.
