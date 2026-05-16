# Self-Audit Reference

Every structured handoff includes a `self_audit` object.

Fields:

| Field | Meaning |
| --- | --- |
| `schema_validated` | The handoff was validated against the `craik.handoff` schema. |
| `redaction_reviewed` | The handoff passed through redaction-aware persistence boundaries. |
| `receipts_reviewed` | The writer checked task receipts and attached receipt ids when available. |
| `assumptions_reviewed` | The writer reviewed case-file assumptions or marked that no case file was available. |
| `validation_recorded` | The handoff records validation in `tests_run`. |
| `policy_exceptions_disclosed` | Policy exceptions and fail-open notes were explicitly recorded, even when none were used. |
| `notes` | Additional self-audit notes. |

Incomplete runs should still produce handoffs. A blocked or incomplete handoff may have `validation_recorded = false`, but it should explain the gap in `risks`, `context_debt`, or `next_steps`.
