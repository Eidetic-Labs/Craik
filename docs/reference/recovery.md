# Recovery Mode

Recovery mode gives a resuming agent a bounded continuity view before it acts.
It summarizes the latest handoff, available case files, receipts, open
contradictions, and active instruction constraints for a project or task.

Recovery mode is a local continuity aid. It does not resolve contradictions,
promote facts, or replace policy checks. A non-clean recovery session tells the
agent what must be reviewed before continuing.

## Contracts

`craik.run_delta` records the continuity-relevant records observed for a
project or task:

- previous and current handoff ids,
- case file ids,
- receipt ids,
- open contradiction ids,
- active promoted instruction constraint ids,
- and a stable list of change items.

`craik.recovery_session` links to a run delta and classifies the resume state:

| Status | Meaning |
| --- | --- |
| `clean_resume` | A latest handoff exists and no blocking changed state was found. |
| `changed_state` | A handoff exists, but open contradictions or active instruction constraints require review. |
| `missing_prior_context` | No prior handoff is available for the requested scope. |

Non-clean recovery sessions must include `required_actions` so an agent does not
silently continue through missing or changed context.

## Boundaries

Recovery summaries are derived from already persisted local store records. They
do not query remote GitHub state, inspect the working tree, or fetch Stigmem
facts by themselves. Callers should refresh those inputs separately, persist the
resulting receipts or contradictions, and then rebuild recovery mode.
