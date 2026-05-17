from pathlib import Path

from craik.contracts.models import DistilledInstructionProposal
from craik.runtime.paths import ensure_craik_home
from craik.runtime.projects.instruction_sources import (
    detect_instruction_contradictions,
    promotable_distilled_instructions,
)
from craik.runtime.store import LocalStore


def _store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def _proposal(
    *,
    proposal_id: str,
    source_id: str,
    category: str,
    statement: str,
) -> DistilledInstructionProposal:
    return DistilledInstructionProposal(
        id=proposal_id,
        project_id="project_docs",
        task_id="task_distill",
        source_id=source_id,
        snapshot_id=f"snapshot_{source_id}",
        category=category,
        statement=statement,
        rationale="Fixture instruction extraction.",
        confidence=0.9,
        provenance_ids=[f"provenance_{proposal_id}"],
        evidence_ids=[f"evidence_{proposal_id}"],
        created_at="2026-05-15T22:30:00Z",
    )


def test_compatible_instructions_do_not_open_contradictions(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        left = _proposal(
            proposal_id="proposal_agents_policy",
            source_id="instruction_source_agents_md",
            category="policy",
            statement="Must run tests before merge.",
        )
        right = _proposal(
            proposal_id="proposal_codex_policy",
            source_id="instruction_source_codex",
            category="policy",
            statement="Should run tests before merge.",
        )
        store.put_distilled_instruction_proposal(left)
        store.put_distilled_instruction_proposal(right)

        reports = detect_instruction_contradictions(store, task_id="task_distill")

        assert reports == []
        assert promotable_distilled_instructions(store.list_distilled_instruction_proposals()) == [
            left,
            right,
        ]
    finally:
        store.close()


def test_conflicting_instructions_open_report_with_source_provenance(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    try:
        left = _proposal(
            proposal_id="proposal_agents_boundary",
            source_id="instruction_source_agents_md",
            category="boundary",
            statement="Must edit generated files.",
        )
        right = _proposal(
            proposal_id="proposal_codex_boundary",
            source_id="instruction_source_codex",
            category="boundary",
            statement="Must not edit generated files.",
        )
        store.put_distilled_instruction_proposal(left)
        store.put_distilled_instruction_proposal(right)

        reports = detect_instruction_contradictions(
            store,
            task_id="task_distill",
            owner="user:maintainer",
        )

        assert len(reports) == 1
        report = reports[0]
        assert report.summary == "Instruction source conflict: boundary"
        assert report.evidence_ids == [
            "provenance_proposal_agents_boundary",
            "provenance_proposal_codex_boundary",
        ]
        assert report.affected_artifacts == [
            left.id,
            right.id,
            left.source_id,
            right.source_id,
        ]
        updated_left = store.get_distilled_instruction_proposal(left.id)
        updated_right = store.get_distilled_instruction_proposal(right.id)
        assert updated_left.promotion_status == "deferred"
        assert updated_right.promotion_status == "deferred"
        assert updated_left.contradiction_ids == [report.id]
        assert updated_right.contradiction_ids == [report.id]
        assert promotable_distilled_instructions([updated_left, updated_right]) == []
    finally:
        store.close()


def test_preference_conflicts_are_preserved_for_later_review_without_reports(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    try:
        store.put_distilled_instruction_proposal(
            _proposal(
                proposal_id="proposal_agents_preference",
                source_id="instruction_source_agents_md",
                category="preference",
                statement="Must use concise summaries.",
            )
        )
        store.put_distilled_instruction_proposal(
            _proposal(
                proposal_id="proposal_codex_preference",
                source_id="instruction_source_codex",
                category="preference",
                statement="Must not use concise summaries.",
            )
        )

        reports = detect_instruction_contradictions(store, task_id="task_distill")

        assert reports == []
        assert store.list_contradictions() == []
    finally:
        store.close()
