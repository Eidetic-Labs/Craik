# Skill Invocation Contexts

Skill invocation contexts define the auditable boundary for one skill run.

The `craik.skill_invocation_context` contract records:

- the task, skill package, policy envelope, and optional handoff linked to the invocation;
- input contracts supplied to the skill;
- expected or produced output contracts;
- omitted context with reason, impact, severity, and mitigation;
- evidence and receipt links;
- redaction status for persisted context.

Skill context is not the skill package itself. The package describes reusable
entrypoints and docs. The invocation context describes what one task actually
handed to the skill, what came back, and what was intentionally or accidentally
left out.

## Boundaries

Skill invocation context must stay policy-linked and redacted. Craik rejects
records without inputs, records with neither outputs nor omissions, and records
that claim unredacted persisted context.

Missing required outputs should be represented as omissions. This makes failed
or partial skill runs reviewable instead of silently treating absent context as
irrelevant.

Use [Skill Telemetry](skill-telemetry.md) to record invocation outcomes,
durations, validation signals, and redacted learning-loop metadata.
