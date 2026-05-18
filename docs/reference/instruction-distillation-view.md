# Instruction Distillation View

The instruction distillation view is a read-only operator display for declared
instruction sources, observed source snapshots, provenance, distilled proposals,
and promotion reviews.

The v0.7.0 TUI surface formats:

- declared instruction sources and their trust boundaries;
- source snapshot hash status;
- provenance records and source ranges;
- distilled instruction proposals by promotion status;
- promotion reviews and their linked receipts, handoffs, and policy envelope.

## Review Flow

Distilled proposals are review records, not active runtime authority. Proposed,
rejected, deferred, stale, and contradicted proposals remain visible so an
operator can audit why an instruction did not become active.

Approved proposals show their promoted constraint ID. Any proposal without a
promoted constraint ID is displayed as inactive, even when it has provenance,
evidence, or prior review notes.

## Trust Boundaries

Sources include their owner and trust boundary. The view preserves those fields
so operators can distinguish repository, project, organization, user, and
external instruction authority before promoting a distilled instruction.

See [Instruction Sources](instruction-sources.md) and
[Instruction Distillation Workflow](instruction-distillation-workflow.md) for
the underlying contract behavior.
