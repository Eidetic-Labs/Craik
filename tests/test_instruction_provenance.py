from pathlib import Path

import pytest
from pydantic import ValidationError

from craik.contracts.models import InstructionProvenance, InstructionSourceSnapshot
from craik.runtime.instruction_sources import (
    render_instruction_provenance_markdown,
    render_instruction_snapshot_json,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore


def _store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def _snapshot(status: str, content_hash: str | None = "abc123") -> InstructionSourceSnapshot:
    return InstructionSourceSnapshot(
        id=f"instruction_snapshot_{status}",
        project_id="project_docs",
        source_id="instruction_source_agents_md",
        path="AGENTS.md",
        content_hash=content_hash,
        hash_status=status,
        byte_count=128 if content_hash else None,
        line_count=12 if content_hash else None,
        captured_at="2026-05-15T22:30:00Z",
    )


@pytest.mark.parametrize("status", ["unchanged", "changed", "new"])
def test_present_instruction_source_hash_states(status: str) -> None:
    snapshot = _snapshot(status)

    assert snapshot.hash_status == status
    assert snapshot.content_hash == "abc123"


def test_missing_instruction_source_hash_state_omits_hash() -> None:
    snapshot = _snapshot("missing", content_hash=None)

    assert snapshot.hash_status == "missing"
    assert snapshot.content_hash is None


def test_snapshot_and_provenance_round_trip(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        snapshot = _snapshot("unchanged")
        provenance = InstructionProvenance(
            id="instruction_provenance_agents_rule",
            project_id="project_docs",
            source_id=snapshot.source_id,
            snapshot_id=snapshot.id,
            path=snapshot.path,
            start_line=3,
            end_line=5,
            start_column=1,
            end_column=80,
            summary="Instruction rule with line-range provenance.",
            excerpt_hash="def456",
            captured_at="2026-05-15T22:31:00Z",
        )

        store.put_instruction_source_snapshot(snapshot)
        store.put_instruction_provenance(provenance)

        assert store.get_instruction_source_snapshot(snapshot.id) == snapshot
        assert store.get_instruction_provenance(provenance.id) == provenance
        assert store.list_instruction_source_snapshots() == [snapshot]
        assert store.list_instruction_provenance() == [provenance]
        assert render_instruction_snapshot_json(snapshot) == render_instruction_snapshot_json(
            InstructionSourceSnapshot.model_validate_json(render_instruction_snapshot_json(snapshot))
        )
        assert "AGENTS.md:3-5" in render_instruction_provenance_markdown(provenance)
    finally:
        store.close()


def test_source_level_provenance_fallback_has_no_range() -> None:
    provenance = InstructionProvenance(
        id="instruction_provenance_source_level",
        project_id="project_docs",
        source_id="instruction_source_agents_md",
        path="AGENTS.md",
        summary="Source-level fallback when line ranges are unavailable.",
        captured_at="2026-05-15T22:31:00Z",
    )

    assert "- Location: AGENTS.md\n" in render_instruction_provenance_markdown(provenance)


def test_missing_sources_reject_hashes() -> None:
    with pytest.raises(ValidationError, match="must not include content_hash"):
        _snapshot("missing", content_hash="abc123")


def test_present_sources_require_hashes() -> None:
    with pytest.raises(ValidationError, match="require content_hash"):
        _snapshot("changed", content_hash=None)


def test_line_ranges_require_start_and_end() -> None:
    with pytest.raises(ValidationError, match="start_line and end_line"):
        InstructionProvenance(
            id="instruction_provenance_invalid",
            project_id="project_docs",
            source_id="instruction_source_agents_md",
            path="AGENTS.md",
            start_line=3,
            summary="Invalid partial range.",
            captured_at="2026-05-15T22:31:00Z",
        )
