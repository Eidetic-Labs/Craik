"""Derived handoff and evidence quality scoring."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.contracts.models import (
    EvidenceCoverageScore,
    Handoff,
    HandoffQualityComponentName,
    HandoffQualityScore,
    QualityScoreBand,
    QualityScoreComponent,
)
from craik.runtime.store import LocalStore


def score_handoff_quality(
    handoff: Handoff,
    *,
    created_at: datetime | None = None,
) -> HandoffQualityScore:
    """Score handoff completeness and recovery value."""
    components = [
        _component("summary", bool(handoff.summary.strip()), 0.12, "Handoff includes a summary."),
        _component(
            "completed_actions",
            bool(handoff.completed_actions),
            0.12,
            "Handoff records completed actions.",
        ),
        _component(
            "validation_records",
            bool(handoff.tests_run) and handoff.self_audit.validation_recorded,
            0.18,
            "Handoff records validation and self-audit confirms it.",
        ),
        _component(
            "receipt_links",
            bool(handoff.receipt_ids) and handoff.self_audit.receipts_reviewed,
            0.14,
            "Handoff links receipts and self-audit confirms review.",
        ),
        _component(
            "evidence_links",
            bool(handoff.artifacts or handoff.adjudication_ids or handoff.receipt_ids),
            0.10,
            "Handoff links evidence-bearing artifacts, adjudications, or receipts.",
        ),
        _component(
            "context_debt",
            not handoff.context_debt,
            0.12,
            "Handoff has no unresolved context debt.",
        ),
        _component(
            "unresolved_risks",
            not handoff.risks and not handoff.unresolved_disagreements,
            0.12,
            "Handoff has no unresolved risks or disagreements.",
        ),
        _component(
            "next_steps",
            bool(handoff.next_steps),
            0.04,
            "Handoff gives a next action for continuation.",
        ),
        _component(
            "self_audit",
            _self_audit_complete(handoff),
            0.16,
            "Handoff self-audit checklist is complete.",
        ),
    ]
    score = _weighted_score(components)
    blocking_reasons = _handoff_blockers(handoff, components)
    return HandoffQualityScore(
        id=f"handoff_quality_{handoff.id}",
        task_id=handoff.task_id,
        project_id=handoff.project_id,
        handoff_id=handoff.id,
        score=score,
        band=_band(score),
        components=components,
        blocking_reasons=blocking_reasons,
        created_at=created_at or datetime.now(UTC),
    )


def score_evidence_coverage(
    *,
    task_id: str,
    evidence_ids: list[str],
    required_evidence_ids: list[str],
    project_id: str | None = None,
    handoff_id: str | None = None,
    weak_claims: list[str] | None = None,
    created_at: datetime | None = None,
) -> EvidenceCoverageScore:
    """Score whether required evidence ids are present."""
    present = set(evidence_ids)
    required = set(required_evidence_ids)
    missing = sorted(required - present)
    if required:
        score = round((len(required) - len(missing)) / len(required), 4)
    else:
        score = 1.0 if evidence_ids else 0.0
    claims = weak_claims or ([] if score >= 0.60 else ["No required evidence was provided."])
    return EvidenceCoverageScore(
        id=f"evidence_coverage_{handoff_id or task_id}",
        task_id=task_id,
        project_id=project_id,
        handoff_id=handoff_id,
        score=score,
        band=_band(score),
        evidence_ids=evidence_ids,
        required_evidence_ids=required_evidence_ids,
        missing_evidence_ids=missing,
        weak_claims=claims,
        created_at=created_at or datetime.now(UTC),
    )


def persist_handoff_scores(
    store: LocalStore,
    handoff: Handoff,
    *,
    evidence_ids: list[str],
    required_evidence_ids: list[str],
) -> tuple[HandoffQualityScore, EvidenceCoverageScore]:
    """Score a handoff and persist both quality contracts."""
    quality = score_handoff_quality(handoff)
    coverage = score_evidence_coverage(
        task_id=handoff.task_id,
        project_id=handoff.project_id,
        handoff_id=handoff.id,
        evidence_ids=evidence_ids,
        required_evidence_ids=required_evidence_ids,
    )
    store.put_handoff_quality_score(quality)
    store.put_evidence_coverage_score(coverage)
    return quality, coverage


def _component(
    name: HandoffQualityComponentName,
    passed: bool,
    weight: float,
    rationale: str,
) -> QualityScoreComponent:
    return QualityScoreComponent(
        name=name,
        score=1.0 if passed else 0.0,
        weight=weight,
        rationale=rationale,
    )


def _self_audit_complete(handoff: Handoff) -> bool:
    audit = handoff.self_audit
    return all(
        [
            audit.schema_validated,
            audit.redaction_reviewed,
            audit.receipts_reviewed,
            audit.assumptions_reviewed,
            audit.validation_recorded,
            audit.policy_exceptions_disclosed,
        ]
    )


def _weighted_score(components: list[QualityScoreComponent]) -> float:
    total_weight = sum(component.weight for component in components)
    weighted = sum(component.score * component.weight for component in components)
    return round(weighted / total_weight, 4)


def _band(score: float) -> QualityScoreBand:
    if score >= 0.85:
        return "excellent"
    if score >= 0.60:
        return "adequate"
    return "poor"


def _handoff_blockers(
    handoff: Handoff,
    components: list[QualityScoreComponent],
) -> list[str]:
    blockers: list[str] = []
    failed = {component.name for component in components if component.score == 0.0}
    if "validation_records" in failed:
        blockers.append("Validation records are missing or not self-audited.")
    if "receipt_links" in failed:
        blockers.append("Receipt links are missing or were not reviewed.")
    if handoff.context_debt:
        blockers.append("Context debt remains unresolved.")
    if handoff.risks or handoff.unresolved_disagreements:
        blockers.append("Unresolved risks or disagreements remain.")
    return blockers
