from pathlib import Path

import pytest
from pydantic import ValidationError

from craik.contracts.models import (
    EvidenceCoverageScore,
    Handoff,
    HandoffQualityScore,
    SelfAudit,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.quality_scores import (
    persist_handoff_scores,
    score_evidence_coverage,
    score_handoff_quality,
)
from craik.runtime.store import LocalStore


def _store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def _audit(validation_recorded: bool = True, receipts_reviewed: bool = True) -> SelfAudit:
    return SelfAudit(
        schema_validated=True,
        redaction_reviewed=True,
        receipts_reviewed=receipts_reviewed,
        assumptions_reviewed=True,
        validation_recorded=validation_recorded,
        policy_exceptions_disclosed=True,
    )


def _handoff(**overrides: object) -> Handoff:
    payload = {
        "id": "handoff_quality",
        "task_id": "task_quality",
        "project_id": "project_quality",
        "agent": "agent:fixture",
        "status": "completed",
        "summary": "Quality handoff completed with evidence.",
        "self_audit": _audit(),
        "completed_actions": ["Implemented scoring."],
        "artifacts": ["artifact_quality"],
        "tests_run": ["pytest"],
        "context_debt": [],
        "risks": [],
        "next_steps": ["Continue with the next issue."],
        "receipt_ids": ["receipt_quality"],
        "created_at": "2026-05-16T09:00:00Z",
    }
    payload.update(overrides)
    return Handoff.model_validate(payload)


def test_high_quality_handoff_scores_excellent(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        handoff = _handoff()
        store.put_handoff(handoff)
        quality, coverage = persist_handoff_scores(
            store,
            handoff,
            evidence_ids=["receipt_quality", "artifact_quality"],
            required_evidence_ids=["receipt_quality", "artifact_quality"],
        )

        assert quality.band == "excellent"
        assert quality.blocking_reasons == []
        assert coverage.band == "excellent"
        assert store.get_handoff_quality_score(quality.id) == quality
        assert store.get_evidence_coverage_score(coverage.id) == coverage
    finally:
        store.close()


def test_incomplete_handoff_scores_poor() -> None:
    handoff = _handoff(
        self_audit=_audit(validation_recorded=False, receipts_reviewed=False),
        completed_actions=[],
        artifacts=[],
        tests_run=[],
        context_debt=["GitHub state was not refreshed."],
        risks=["Validation is incomplete."],
        next_steps=[],
        receipt_ids=[],
    )

    score = score_handoff_quality(handoff)

    assert score.band == "poor"
    assert "Validation records are missing or not self-audited." in score.blocking_reasons
    assert "Context debt remains unresolved." in score.blocking_reasons


def test_evidence_poor_handoff_scores_poor() -> None:
    score = score_evidence_coverage(
        task_id="task_quality",
        project_id="project_quality",
        handoff_id="handoff_quality",
        evidence_ids=["receipt_quality"],
        required_evidence_ids=["receipt_quality", "artifact_quality", "adjudication_quality"],
        weak_claims=["The handoff cites validation without an artifact link."],
    )

    assert score.band == "poor"
    assert score.missing_evidence_ids == ["adjudication_quality", "artifact_quality"]
    assert score.weak_claims == ["The handoff cites validation without an artifact link."]


def test_score_contract_bands_must_match_numeric_score() -> None:
    handoff_score = score_handoff_quality(_handoff())
    with pytest.raises(ValidationError, match="must be excellent"):
        HandoffQualityScore.model_validate(
            handoff_score.model_dump(mode="json", by_alias=True) | {"band": "adequate"}
        )

    evidence_score = score_evidence_coverage(
        task_id="task_quality",
        evidence_ids=["evidence_quality"],
        required_evidence_ids=["evidence_quality"],
    )
    with pytest.raises(ValidationError, match="must be excellent"):
        EvidenceCoverageScore.model_validate(
            evidence_score.model_dump(mode="json", by_alias=True) | {"band": "adequate"}
        )
