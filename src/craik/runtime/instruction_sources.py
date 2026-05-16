"""Instruction source provenance rendering helpers."""

from __future__ import annotations

from craik.contracts.models import (
    DistilledInstructionProposal,
    InstructionProvenance,
    InstructionSourceSnapshot,
)
from craik.runtime.store import LocalStore


def render_instruction_snapshot_json(snapshot: InstructionSourceSnapshot) -> str:
    """Render a deterministic JSON representation of an instruction snapshot."""
    return snapshot.model_dump_json(by_alias=True, exclude_none=True, indent=2) + "\n"


def render_instruction_provenance_markdown(provenance: InstructionProvenance) -> str:
    """Render deterministic Markdown for instruction source provenance."""
    if provenance.start_line is None:
        location = provenance.path
    else:
        location = f"{provenance.path}:{provenance.start_line}-{provenance.end_line}"
    lines = [
        f"# Instruction Provenance: {provenance.id}",
        "",
        f"- Source: {provenance.source_id}",
        f"- Snapshot: {provenance.snapshot_id or 'none'}",
        f"- Location: {location}",
        f"- Summary: {provenance.summary}",
    ]
    if provenance.excerpt_hash:
        lines.append(f"- Excerpt Hash: {provenance.excerpt_hash}")
    return "\n".join(lines) + "\n"


def render_distilled_instruction_markdown(proposal: DistilledInstructionProposal) -> str:
    """Render deterministic Markdown for a distilled instruction proposal."""
    lines = [
        f"# Distilled Instruction: {proposal.id}",
        "",
        f"- Category: {proposal.category}",
        f"- Promotion Status: {proposal.promotion_status}",
        f"- Source: {proposal.source_id}",
        f"- Confidence: {proposal.confidence:.2f}",
        f"- Statement: {proposal.statement}",
        f"- Rationale: {proposal.rationale}",
        "- Provenance:",
        *_bullet_lines(proposal.provenance_ids),
        "- Evidence:",
        *_bullet_lines(proposal.evidence_ids),
    ]
    if proposal.contradiction_ids:
        lines.extend(["- Contradictions:", *_bullet_lines(proposal.contradiction_ids)])
    return "\n".join(lines) + "\n"


def render_distilled_instruction_json(proposal: DistilledInstructionProposal) -> str:
    """Render deterministic JSON for a distilled instruction proposal."""
    return proposal.model_dump_json(by_alias=True, exclude_none=True, indent=2) + "\n"


def invalidate_stale_distillations(
    store: LocalStore,
    *,
    current_snapshots: list[InstructionSourceSnapshot],
    decided_by: str = "agent:instruction-distillation",
) -> list[DistilledInstructionProposal]:
    """Mark proposals stale when their source snapshot changed, disappeared, or is new."""
    previous_by_source = {
        snapshot.source_id: snapshot for snapshot in store.list_instruction_source_snapshots()
    }
    stale_source_ids = _stale_source_ids(previous_by_source, current_snapshots)
    if not stale_source_ids:
        for snapshot in current_snapshots:
            store.put_instruction_source_snapshot(snapshot)
        return []

    invalidated: list[DistilledInstructionProposal] = []
    for proposal in store.list_distilled_instruction_proposals():
        if proposal.source_id not in stale_source_ids or proposal.promotion_status == "rejected":
            continue
        updated = proposal.model_copy(
            update={
                "promotion_status": "deferred",
                "decided_by": decided_by,
                "decided_at": max(snapshot.captured_at for snapshot in current_snapshots),
            }
        )
        updated = DistilledInstructionProposal.model_validate(
            updated.model_dump(mode="json", by_alias=True)
        )
        store.put_distilled_instruction_proposal(updated)
        invalidated.append(updated)

    for snapshot in current_snapshots:
        store.put_instruction_source_snapshot(snapshot)
    return sorted(invalidated, key=lambda proposal: proposal.id)


def instruction_stale_risk_warnings(store: LocalStore, project_id: str) -> list[str]:
    """Return stale-risk warnings for deferred instruction proposals in a project."""
    warnings = []
    for proposal in store.list_distilled_instruction_proposals():
        if proposal.project_id != project_id or proposal.promotion_status != "deferred":
            continue
        warnings.append(
            f"Instruction distillation {proposal.id} from {proposal.source_id} is stale; "
            "review provenance before promotion."
        )
    return sorted(set(warnings))


def promotable_distilled_instructions(
    proposals: list[DistilledInstructionProposal],
) -> list[DistilledInstructionProposal]:
    """Return proposals eligible for automatic promotion review."""
    return sorted(
        (
            proposal
            for proposal in proposals
            if proposal.promotion_status == "proposed" and not proposal.contradiction_ids
        ),
        key=lambda proposal: proposal.id,
    )


def _bullet_lines(values: list[str]) -> list[str]:
    if not values:
        return ["  - None"]
    return [f"  - {value}" for value in values]


def _stale_source_ids(
    previous_by_source: dict[str, InstructionSourceSnapshot],
    current_snapshots: list[InstructionSourceSnapshot],
) -> set[str]:
    stale = set()
    current_by_source = {snapshot.source_id: snapshot for snapshot in current_snapshots}
    for source_id, current in current_by_source.items():
        previous = previous_by_source.get(source_id)
        if previous is None:
            stale.add(source_id)
            continue
        if current.hash_status in {"changed", "missing", "new"}:
            stale.add(source_id)
            continue
        if current.content_hash != previous.content_hash:
            stale.add(source_id)
    for source_id in set(previous_by_source) - set(current_by_source):
        stale.add(source_id)
    return stale
