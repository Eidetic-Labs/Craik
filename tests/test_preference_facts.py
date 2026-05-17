from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.memory.preference_facts import PreferenceFact, review_preference_fact

NOW = datetime(2026, 5, 16, 21, 20, tzinfo=UTC)


def _preference(**overrides: object) -> PreferenceFact:
    payload = {
        "id": "preference_user_pr_titles",
        "subject": "user:maintainer",
        "scope": "user",
        "statement": "Use standard PR titles without tool prefixes.",
        "status": "inferred",
        "confidence": 0.72,
        "evidence_ids": ["evidence_pr_title_request"],
        "receipt_ids": ["receipt_preference_inferred"],
        "inferred_from": ["issue_comment_pr_title"],
        "created_at": NOW,
    }
    payload.update(overrides)
    return PreferenceFact.model_validate(payload)


def test_preference_fact_records_inferred_user_preference() -> None:
    preference = _preference()

    assert preference.status == "inferred"
    assert preference.scope == "user"
    assert preference.reviewed_by is None
    assert preference.inferred_from == ["issue_comment_pr_title"]


def test_review_preference_fact_approves_inferred_preference() -> None:
    reviewed = review_preference_fact(
        _preference(),
        status="approved",
        reviewed_by="user:maintainer",
        review_reason="Matches explicit user instruction.",
        reviewed_at=NOW,
    )

    assert reviewed.status == "approved"
    assert reviewed.reviewed_by == "user:maintainer"
    assert reviewed.review_reason == "Matches explicit user instruction."
    assert reviewed.reviewed_at == NOW


def test_review_preference_fact_rejects_inferred_preference() -> None:
    reviewed = review_preference_fact(
        _preference(statement="Always skip CI."),
        status="rejected",
        reviewed_by="user:maintainer",
        review_reason="Contradicts repository workflow.",
        reviewed_at=NOW,
    )

    assert reviewed.status == "rejected"
    assert reviewed.review_reason == "Contradicts repository workflow."


def test_preference_fact_enforces_subject_scope_boundaries() -> None:
    with pytest.raises(ValidationError, match="user subject"):
        _preference(subject="team:platform")

    with pytest.raises(ValidationError, match="team subject"):
        _preference(scope="team", subject="user:maintainer")


def test_preference_fact_requires_evidence_receipts_and_review_fields() -> None:
    with pytest.raises(ValidationError):
        _preference(evidence_ids=[])

    with pytest.raises(ValidationError):
        _preference(receipt_ids=[])

    with pytest.raises(ValidationError, match="inferred_from"):
        _preference(inferred_from=[])

    with pytest.raises(ValidationError, match="review fields"):
        _preference(status="approved")


def test_inferred_preference_cannot_carry_review_fields() -> None:
    with pytest.raises(ValidationError, match="must not include review fields"):
        _preference(reviewed_by="user:maintainer")
