# Runtime Instruction Distillation Workflow

Runtime instruction distillation turns declared instruction files into reviewed,
provenance-linked runtime constraints. Raw instruction files are evidence, not
automatic authority.

## Workflow

1. Register declared sources with `craik.instruction_source_registry`.
2. Capture source identity with `craik.instruction_source_snapshot`.
3. Link extracted text with `craik.instruction_provenance`.
4. Create reviewable `craik.distilled_instruction_proposal` records.
5. Invalidate proposals when source snapshots change, go missing, are new, or
   are omitted from the current scan.
6. Open `craik.contradiction_report` records when authoritative instruction
   proposals conflict across sources.
7. Record `craik.instruction_promotion_review` decisions.
8. Create `craik.promoted_instruction_constraint` only for approved proposals.
9. Consume active constraints in case files, prompts, onboarding, and handoffs.

## Operator Rules

- Proposed distillations are inactive until approved.
- Stale, contradicted, rejected, and deferred distillations remain visible but
  inactive.
- Active constraints must retain source ID, source snapshot ID, provenance IDs,
  evidence IDs, and review links.
- Case files and onboarding reports surface stale-risk warnings instead of
  treating stale distillations as facts.
- Handoffs carry active instruction constraint IDs forward so later agents can
  audit what shaped the run.

## Fixtures

The contract fixture file includes examples for the core v0.4.0 records:

- `craik.instruction_source`
- `craik.instruction_source_registry`
- `craik.instruction_source_snapshot`
- `craik.instruction_provenance`
- `craik.distilled_instruction_proposal`
- `craik.instruction_promotion_review`
- `craik.promoted_instruction_constraint`

Runtime tests cover stale invalidation, contradiction handling, promotion
review, and active-context consumption.
