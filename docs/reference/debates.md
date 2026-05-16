# Structured Debates

Structured debates capture bounded multi-agent disagreement without erasing
minority positions. They are coordination records, not a consensus mechanism.

## Contracts

`craik.debate_turn` records one role-linked contribution:

- `role_id` and `role_kind` identify the specialist or adjudicator speaking.
- `worker_result_id` links the turn back to typed specialist output when one
  exists.
- `position` records whether the turn supports, opposes, clarifies, questions,
  or blocks the topic.
- `evidence_ids`, `assumption_ids`, and `contradiction_ids` preserve the basis
  and unresolved review work behind the claim.

`craik.debate_summary` records the deterministic outcome for a debate:

- `agreement` means support turns reached the same bounded conclusion and no
  opposing or blocking turn remains.
- `unresolved_disagreement` preserves a conflict without opening a contradiction
  report. Use this when the orchestrator needs human or adjudicator review but
  the disagreement is not yet known to be an incompatible factual assertion.
- `contradiction_opened` links to one or more `craik.contradiction_report`
  records. Use this when specialist outputs assert incompatible facts or
  mutually exclusive implementation status.

## Boundaries

Debate turns must stay scoped to the task and topic. A turn can cite evidence or
assumptions, but it must not promote assumptions to facts. A debate summary can
list next steps, but it must not silently choose a winner when a blocker or
opposing specialist output remains unresolved.

## Rendering

Markdown and JSON rendering are deterministic. Renderers keep turn order from
`turn_ids`, sort evidence-style lists where order has no semantic meaning, and
emit explicit `None` rows for empty sections so absent agreement or contradiction
links are visible in review.
