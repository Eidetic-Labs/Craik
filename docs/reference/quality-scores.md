# Quality Scores

Craik quality scores are derived review records. They help agents decide whether
a handoff or evidence set is ready to rely on, but they are not proof of truth or
permission to skip policy review.

## Handoff Quality

`craik.handoff_quality_score` summarizes whether a handoff is useful for
continuation. Inputs include:

- summary and completed actions,
- validation records,
- linked receipts,
- evidence-bearing artifacts, adjudications, or receipts,
- context debt,
- unresolved risks and disagreements,
- next steps,
- and the self-audit checklist.

Scores are normalized from `0.0` to `1.0` and mapped to:

| Band | Range |
| --- | --- |
| `excellent` | `0.85` to `1.0` |
| `adequate` | `0.60` to less than `0.85` |
| `poor` | less than `0.60` |

Poor handoff scores must include `blocking_reasons` so a resuming agent knows
what to repair.

## Evidence Coverage

`craik.evidence_coverage_score` compares evidence ids present in a handoff or
output with evidence ids required by the caller. Missing ids and weak claims are
preserved explicitly.

Evidence coverage is not a certainty score. A complete set of links means the
expected references are present, not that the underlying claims are true.
