# Skill Telemetry

Skill performance telemetry records how one skill invocation behaved without
allowing the agent to silently rewrite reusable guidance.

`SkillPerformanceTelemetry` records:

- telemetry id;
- task id;
- skill package id;
- skill invocation context id;
- outcome: `succeeded`, `failed`, or `partial`;
- duration in milliseconds;
- validation signals;
- evidence ids;
- receipt ids;
- policy envelope id;
- redacted metadata;
- creation timestamp.

Failed telemetry requires at least one failed validation signal. All telemetry
requires policy and receipt links.

## Redaction

Telemetry metadata must not persist raw prompts, inputs, outputs, traces,
stdout, stderr, raw errors, responses, payloads, credentials, tokens, passwords,
or API keys.

Use telemetry for learning-loop evidence, not as authority to change a skill.
Later proposals and promotion gates should cite telemetry alongside receipts,
evidence, and review decisions.

Use [Skill Proposals](skill-proposals.md) to draft reviewable changes from
telemetry.
