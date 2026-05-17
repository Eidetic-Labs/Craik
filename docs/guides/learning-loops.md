# Learning Loops

Craik learning loops turn observed skill behavior into reviewable improvement
records. They do not let an agent silently rewrite reusable guidance.

The supported flow is:

1. Record [Skill Telemetry](../reference/skill-telemetry.md) for an invocation.
2. Draft a [Skill Proposal](../reference/skill-proposals.md) from telemetry,
   evidence, and receipts.
3. Run [Skill Replay](../reference/skill-replay.md) against redacted fixtures.
4. Record review, replay, promotion, rollback, export, and other decisions with
   [Learning Receipts](../reference/learning-receipts.md).
5. Apply [Skill Promotion Gates](../reference/skill-promotion-gates.md) before
   promoted guidance changes.
6. Use [Skill Rollbacks](../reference/skill-rollbacks.md) when a promoted
   version regresses.
7. Use [Training Trajectory Exports](../reference/trajectory-exports.md) and
   compressed summaries for replay and review.

Learning loops can also use [Memory Review Nudges](../reference/memory-review-nudges.md)
and [Preference Facts](../reference/preference-facts.md) when repeated behavior
suggests a reviewable memory update or preference clarification.

## Evidence Boundary

Every learning-loop step should preserve ids instead of raw payloads:

- task ids;
- policy envelope ids;
- evidence ids;
- receipt ids;
- telemetry ids;
- replay fixture ids;
- replay result ids;
- proposal ids;
- promoted version ids;
- rollback version ids;
- unresolved risk ids.

Telemetry, receipts, proposals, exports, and summaries must redact secrets,
private prompts, private payloads, raw outputs, traces, trajectories,
credentials, and local-only filesystem paths.

## Promotion Requirements

A skill proposal can become promoted guidance only after explicit approval.
Promotion requires:

- an approved proposal;
- a structured improvement plan;
- a non-agent approver;
- policy envelope context;
- evidence ids;
- eval or replay result ids;
- receipt ids;
- an approval receipt id.

Missing promotion gates produce a denied promotion decision. Denied decisions
are useful review artifacts and should keep explicit denial reasons.

## Rollback Requirements

Rollbacks target a prior promoted version. A rollback decision should preserve:

- the promoted version id;
- the rollback version id;
- rollback reason and rationale;
- policy envelope context;
- evidence ids;
- receipt ids;
- replay result ids;
- the rollback decision receipt.

Rollback decisions should not invent replacement guidance. They move back to a
known prior version and leave an audit trail.

## Trajectory Review

Training trajectory exports are redacted replay and review artifacts. Full
exports keep decision-level detail, while compressed summaries keep the links
needed for review:

- receipt ids;
- evidence ids;
- policy envelope ids;
- replay fixture ids;
- replay result ids;
- unresolved risk ids.

Compressed summaries omit decision detail by design. Load the source export when
reviewers need diagnostics, artifacts, observed output, or per-step timestamps.

## Safe Diagnostics

Use repository validation commands that do not print secrets or private local
state:

```sh
uv run --extra dev ruff check .
uv run --extra dev mypy
uv run --extra dev pytest tests/test_skill_telemetry.py tests/test_skill_proposals.py tests/test_skill_replay.py
uv run --extra dev pytest tests/test_learning_receipts.py tests/test_skill_promotions.py tests/test_skill_rollbacks.py
uv run --extra dev pytest tests/test_trajectory_exports.py tests/test_docs.py
```

Expected successful output includes:

```text
All checks passed!
Success: no issues found
passed
```

If a command fails, preserve the command, failing test name, and sanitized error
summary in a receipt or review note. Do not copy raw prompts, credentials,
private payloads, or local-only paths into public docs.
