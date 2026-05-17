import pytest

from craik.contracts.models import DistilledInstructionProposal
from craik.runtime.paths import ensure_craik_home
from craik.runtime.projects.instruction_sources import (
    InstructionPromotionError,
    review_instruction_promotion,
)
from craik.runtime.store import LocalStore


def _store(tmp_path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def _proposal(snapshot_id: str | None = "snapshot_agents") -> DistilledInstructionProposal:
    return DistilledInstructionProposal(
        id="distilled_instruction_agents_rule",
        project_id="project_docs",
        source_id="instruction_source_agents_md",
        snapshot_id=snapshot_id,
        category="instruction",
        statement="Run tests before merge.",
        rationale="Extracted from AGENTS.md.",
        confidence=0.9,
        provenance_ids=["provenance_agents_rule"],
        evidence_ids=["evidence_agents_rule"],
        created_at="2026-05-15T22:30:00Z",
    )


def test_approved_promotion_creates_active_constraint_and_audit_links(tmp_path) -> None:
    store = _store(tmp_path)
    try:
        proposal = _proposal()
        store.put_distilled_instruction_proposal(proposal)

        review = review_instruction_promotion(
            store,
            proposal_id=proposal.id,
            decision="approved",
            decided_by="user:maintainer",
            rationale="Instruction is valid.",
            policy_envelope_id="policy_distill",
            receipt_ids=["receipt_review"],
            memory_proposal_ids=["proposal_memory"],
            handoff_ids=["handoff_distill"],
        )

        updated = store.get_distilled_instruction_proposal(proposal.id)
        constraint = store.get_promoted_instruction_constraint(review.promoted_constraint_id)
        assert review.decision == "approved"
        assert updated.promotion_status == "approved"
        assert updated.promoted_constraint_id == constraint.id
        assert constraint.active is True
        assert constraint.snapshot_id == proposal.snapshot_id
        assert constraint.provenance_ids == proposal.provenance_ids
        assert constraint.receipt_ids == ["receipt_review"]
        assert store.list_instruction_promotion_reviews() == [review]
        assert store.list_promoted_instruction_constraints() == [constraint]
    finally:
        store.close()


@pytest.mark.parametrize("decision", ["rejected", "deferred"])
def test_unapproved_promotion_decisions_are_persisted_without_constraints(
    tmp_path,
    decision: str,
) -> None:
    store = _store(tmp_path)
    try:
        proposal = _proposal()
        store.put_distilled_instruction_proposal(proposal)

        review = review_instruction_promotion(
            store,
            proposal_id=proposal.id,
            decision=decision,
            decided_by="user:maintainer",
            rationale=f"Promotion {decision}.",
            receipt_ids=["receipt_review"],
        )

        updated = store.get_distilled_instruction_proposal(proposal.id)
        assert review.decision == decision
        assert review.promoted_constraint_id is None
        assert updated.promotion_status == decision
        assert updated.promoted_constraint_id is None
        assert store.list_promoted_instruction_constraints() == []
    finally:
        store.close()


def test_approved_promotion_requires_source_snapshot(tmp_path) -> None:
    store = _store(tmp_path)
    try:
        proposal = _proposal(snapshot_id=None)
        store.put_distilled_instruction_proposal(proposal)

        with pytest.raises(InstructionPromotionError, match="source snapshot"):
            review_instruction_promotion(
                store,
                proposal_id=proposal.id,
                decision="approved",
                decided_by="user:maintainer",
                rationale="Cannot approve without snapshot.",
            )
    finally:
        store.close()


def test_unknown_promotion_proposal_raises(tmp_path) -> None:
    store = _store(tmp_path)
    try:
        with pytest.raises(InstructionPromotionError, match="unknown"):
            review_instruction_promotion(
                store,
                proposal_id="missing",
                decision="approved",
                decided_by="user:maintainer",
                rationale="Missing.",
            )
    finally:
        store.close()
