from pathlib import Path

from craik.contracts.models import DebateSummary, DebateTurn
from craik.runtime.paths import ensure_craik_home
from craik.runtime.reviewing.debates import (
    DebateManager,
    render_debate_json,
    render_debate_markdown,
)
from craik.runtime.store import LocalStore


def _store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def _turn(
    *,
    turn_id: str,
    position: str,
    role_id: str,
    claim: str,
    worker_result_id: str | None = None,
) -> DebateTurn:
    return DebateTurn(
        id=turn_id,
        task_id="task_debate",
        debate_id="debate_architecture",
        role_id=role_id,
        role_kind="verifier",
        worker_result_id=worker_result_id,
        position=position,
        claim=claim,
        rationale=f"Rationale for {turn_id}.",
        evidence_ids=[f"evidence_{turn_id}"],
        assumption_ids=[f"assumption_{turn_id}"],
        created_at="2026-05-15T22:30:00Z",
    )


def test_debate_agreement_summary_and_deterministic_rendering(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        manager = DebateManager(store)
        turns = [
            _turn(
                turn_id="turn_docs",
                position="supports",
                role_id="role_docs",
                claim="The docs match the implementation.",
            ),
            _turn(
                turn_id="turn_verifier",
                position="supports",
                role_id="role_verifier",
                claim="The docs match the implementation.",
            ),
        ]

        summary = manager.summarize(
            task_id="task_debate",
            debate_id="debate_architecture",
            topic="documentation status",
            turns=turns,
        )

        assert summary.outcome == "agreement"
        assert summary.agreements == ["The docs match the implementation."]
        assert summary.contradiction_ids == []
        markdown = render_debate_markdown(summary, turns)
        assert markdown == render_debate_markdown(summary, list(reversed(turns)))
        assert "- Outcome: agreement" in markdown
        assert render_debate_json(summary) == render_debate_json(
            DebateSummary.model_validate_json(render_debate_json(summary))
        )
    finally:
        store.close()


def test_debate_preserves_unresolved_disagreement_without_forcing_consensus(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    try:
        turns = [
            _turn(
                turn_id="turn_support",
                position="supports",
                role_id="role_verifier",
                claim="The implementation is complete.",
            ),
            _turn(
                turn_id="turn_oppose",
                position="opposes",
                role_id="role_adversarial",
                claim="The implementation lacks deterministic rendering.",
            ),
        ]

        summary = DebateManager(store).summarize(
            task_id="task_debate",
            debate_id="debate_architecture",
            topic="implementation completeness",
            turns=turns,
            open_contradictions=False,
        )

        assert summary.outcome == "unresolved_disagreement"
        assert summary.agreements == []
        assert summary.unresolved_disagreements
        assert summary.contradiction_ids == []
        assert store.list_contradictions() == []
    finally:
        store.close()


def test_debate_opens_contradiction_report_for_conflicting_specialist_outputs(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    try:
        turns = [
            _turn(
                turn_id="turn_support",
                position="supports",
                role_id="role_verifier",
                claim="The implementation is complete.",
                worker_result_id="worker_result_verifier",
            ),
            _turn(
                turn_id="turn_block",
                position="blocks",
                role_id="role_adversarial",
                claim="The implementation lacks deterministic rendering.",
                worker_result_id="worker_result_adversarial",
            ),
        ]

        summary = DebateManager(store).summarize(
            task_id="task_debate",
            debate_id="debate_architecture",
            topic="implementation completeness",
            turns=turns,
            open_contradictions=True,
        )

        reports = store.list_contradictions()
        assert summary.outcome == "contradiction_opened"
        assert summary.contradiction_ids == [reports[0].id]
        assert reports[0].summary == "Debate disagreement: implementation completeness"
        assert reports[0].affected_artifacts == [
            "worker_result_adversarial",
            "worker_result_verifier",
        ]
    finally:
        store.close()
