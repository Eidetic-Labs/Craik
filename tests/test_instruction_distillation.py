from pathlib import Path

import pytest
from pydantic import ValidationError

from craik.contracts.models import DistilledInstructionProposal
from craik.runtime.instruction_sources import (
    render_distilled_instruction_json,
    render_distilled_instruction_markdown,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore

REQUIRED_CATEGORIES = [
    "instruction",
    "policy",
    "preference",
    "command",
    "boundary",
    "handoff_rule",
    "memory_rule",
    "security_rule",
    "stale_risk",
]


def _store(tmp_path: Path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def _proposal(category: str, evidence_ids: list[str] | None = None) -> DistilledInstructionProposal:
    return DistilledInstructionProposal(
        id=f"distilled_instruction_{category}",
        project_id="project_docs",
        task_id="task_distill",
        source_id="instruction_source_agents_md",
        snapshot_id="instruction_snapshot_agents_md",
        category=category,
        statement=f"Fixture {category} statement.",
        rationale=f"Fixture {category} rationale.",
        confidence=0.82,
        provenance_ids=["instruction_provenance_agents_rule"],
        evidence_ids=evidence_ids if evidence_ids is not None else ["evidence_agents_md"],
        created_at="2026-05-15T22:30:00Z",
    )


@pytest.mark.parametrize("category", REQUIRED_CATEGORIES)
def test_distilled_instruction_proposal_supports_required_categories(category: str) -> None:
    proposal = _proposal(category)

    assert proposal.category == category
    assert proposal.promotion_status == "proposed"
    assert proposal.provenance_ids == ["instruction_provenance_agents_rule"]


def test_distilled_instruction_proposal_round_trips_and_renders(tmp_path: Path) -> None:
    store = _store(tmp_path)
    try:
        proposal = _proposal("boundary")

        store.put_distilled_instruction_proposal(proposal)

        assert store.get_distilled_instruction_proposal(proposal.id) == proposal
        assert store.list_distilled_instruction_proposals() == [proposal]
        markdown = render_distilled_instruction_markdown(proposal)
        assert "- Category: boundary" in markdown
        assert "instruction_provenance_agents_rule" in markdown
        assert render_distilled_instruction_json(proposal) == render_distilled_instruction_json(
            DistilledInstructionProposal.model_validate_json(
                render_distilled_instruction_json(proposal)
            )
        )
    finally:
        store.close()


def test_distilled_instruction_proposals_require_provenance() -> None:
    with pytest.raises(ValidationError, match="at least 1 item"):
        DistilledInstructionProposal(
            id="distilled_instruction_missing_provenance",
            project_id="project_docs",
            source_id="instruction_source_agents_md",
            category="instruction",
            statement="Missing provenance.",
            rationale="No provenance should fail validation.",
            confidence=0.5,
            provenance_ids=[],
            created_at="2026-05-15T22:30:00Z",
        )


def test_policy_and_security_rule_distillations_require_evidence() -> None:
    with pytest.raises(ValidationError, match="require evidence ids"):
        _proposal("policy", evidence_ids=[])
    with pytest.raises(ValidationError, match="require evidence ids"):
        _proposal("security_rule", evidence_ids=[])


def test_approved_distillation_requires_review_metadata() -> None:
    with pytest.raises(ValidationError, match="promoted_constraint_id"):
        DistilledInstructionProposal(
            id="distilled_instruction_approved_without_constraint",
            project_id="project_docs",
            source_id="instruction_source_agents_md",
            category="instruction",
            statement="Approved instruction.",
            rationale="Needs promoted constraint.",
            confidence=0.9,
            provenance_ids=["instruction_provenance_agents_rule"],
            promotion_status="approved",
            decided_by="user:maintainer",
            decided_at="2026-05-15T22:31:00Z",
            created_at="2026-05-15T22:30:00Z",
        )

    with pytest.raises(ValidationError, match="reviewer and decision time"):
        DistilledInstructionProposal(
            id="distilled_instruction_approved",
            project_id="project_docs",
            source_id="instruction_source_agents_md",
            category="instruction",
            statement="Approved instruction.",
            rationale="Needs review metadata.",
            confidence=0.9,
            provenance_ids=["instruction_provenance_agents_rule"],
            promotion_status="approved",
            promoted_constraint_id="constraint_agents_rule",
            created_at="2026-05-15T22:30:00Z",
        )
