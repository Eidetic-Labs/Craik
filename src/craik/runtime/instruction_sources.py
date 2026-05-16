"""Instruction source provenance rendering helpers."""

from __future__ import annotations

from craik.contracts.models import InstructionProvenance, InstructionSourceSnapshot


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
