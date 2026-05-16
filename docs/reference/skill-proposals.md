# Skill Proposals

Skill proposals let agents draft changes to reusable operating guidance without
silently changing their own authority.

`SkillChangeProposal` records:

- proposal id;
- skill package id;
- task id;
- title, summary, rationale, and proposed change;
- source: `telemetry`, `operator`, or `review`;
- status: `pending_review`, `approved`, or `rejected`;
- policy envelope id;
- evidence ids;
- telemetry ids;
- receipt ids;
- creator and creation timestamp.

Agent-created proposals must remain `pending_review`. Review and promotion are
separate gates.

Telemetry-sourced proposals require telemetry ids so reviewers can inspect the
observed behavior that motivated the proposed change.

## Boundary

Skill proposals are not skill updates. They are reviewable records that can be
cited by later approval gates, eval/replay checks, rollback plans, and learning
loop receipts.
