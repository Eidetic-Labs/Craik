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
- optional structured improvement plan;
- creator and creation timestamp.

Agent-created proposals must remain `pending_review`. Review and promotion are
separate gates.

Telemetry-sourced proposals require telemetry ids so reviewers can inspect the
observed behavior that motivated the proposed change.

## Boundary

Skill proposals are not skill updates. They are reviewable records that can be
cited by later approval gates, eval/replay checks, rollback plans, and learning
loop receipts.

Use [Skill Replay](skill-replay.md) to compare current skill behavior against
redacted fixtures before promotion.

## Improvement Plans

`SkillImprovementPlan` adds structured review details:

- expected benefit;
- risk: `low`, `medium`, `high`, or `critical`;
- rollback notes;
- proposed edit targets;
- replay fixture ids.

High-risk and critical improvements require replay fixture ids. Approved
proposals require an improvement plan so reviewers can inspect benefit, risk,
edit scope, and rollback path before promotion.
