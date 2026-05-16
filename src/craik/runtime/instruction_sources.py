"""Instruction source provenance rendering helpers."""

from __future__ import annotations

from craik.contracts.models import (
    DistilledInstructionProposal,
    InstructionProvenance,
    InstructionSourceSnapshot,
)


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


def _bullet_lines(values: list[str]) -> list[str]:
    if not values:
        return ["  - None"]
    return [f"  - {value}" for value in values]
