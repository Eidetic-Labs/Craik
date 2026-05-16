# Agent Roles

`craik.agent_role` defines the role boundary for v0.4.0 multi-agent
coordination. Roles describe responsibility and authority; they do not grant new
runtime permissions by themselves.

Supported role kinds:

| Kind | Responsibility |
| --- | --- |
| `orchestrator` | Coordinate specialists, preserve outputs, and decide routing. |
| `implementer` | Produce scoped implementation work. |
| `verifier` | Validate behavior, tests, and acceptance criteria. |
| `adversarial_reviewer` | Look for failure modes, regressions, and weak assumptions. |
| `policy_reviewer` | Check policy, grants, receipts, and redaction boundaries. |
| `docs_reviewer` | Review documentation, operator instructions, and examples. |
| `memory_curator` | Review memory proposals, stale risks, and contradiction boundaries. |
| `adjudicator` | Decide between reviewed outputs or defer unresolved disagreements. |

Role authority values are explicit: `coordinate`, `read`, `propose`, `review`,
`adjudicate`, and `implement`. Policy envelopes and capability grants still
control side effects.

Each role records expected input schemas, expected output schemas, handoff and
receipt obligations, redaction requirements, and optional runner identity. This
keeps roles compatible with runner metadata while preserving policy boundaries.
