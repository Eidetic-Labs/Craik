from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.runtime.memory_review import (
    MemoryReviewCandidate,
    MemoryReviewNudge,
    memory_review_nudge,
)

NOW = datetime(2026, 5, 16, 21, 15, tzinfo=UTC)


def _candidate(**overrides: object) -> MemoryReviewCandidate:
    payload = {
        "fact_ref": "fact_memory_policy",
        "entity": "repo:craik",
        "relation": "craik:memory_policy",
        "scope": "local",
        "confidence": 0.8,
        "evidence_ids": ["evidence_memory_policy"],
        "last_reviewed_at": datetime(2026, 5, 15, 21, 15, tzinfo=UTC),
        "owner": "user:maintainer",
    }
    payload.update(overrides)
    return MemoryReviewCandidate.model_validate(payload)


def test_memory_review_nudge_not_due_for_recent_supported_fact() -> None:
    nudge = memory_review_nudge(
        nudge_id="memory_review_recent",
        candidate=_candidate(),
        now=NOW,
        review_interval_days=7,
        receipt_ids=["receipt_memory_review"],
    )

    assert nudge.status == "not_due"
    assert nudge.reasons == []
    assert nudge.owner == "user:maintainer"


def test_memory_review_nudge_due_for_stale_fact() -> None:
    nudge = memory_review_nudge(
        nudge_id="memory_review_stale",
        candidate=_candidate(last_reviewed_at=datetime(2026, 5, 1, 21, 15, tzinfo=UTC)),
        now=NOW,
        review_interval_days=7,
        receipt_ids=["receipt_memory_review"],
    )

    assert nudge.status == "due"
    assert nudge.reasons == ["stale"]
    assert nudge.due_at == NOW
    assert nudge.receipt_ids == ["receipt_memory_review"]


def test_memory_review_nudge_due_for_multiple_review_risks() -> None:
    nudge = memory_review_nudge(
        nudge_id="memory_review_risky",
        candidate=_candidate(
            confidence=0.2,
            evidence_ids=[],
            expires_at=datetime(2026, 5, 16, 20, 0, tzinfo=UTC),
        ),
        now=NOW,
        review_interval_days=7,
        min_confidence=0.5,
        receipt_ids=["receipt_memory_review"],
    )

    assert nudge.status == "due"
    assert nudge.reasons == ["expiring", "low_confidence", "missing_evidence"]


def test_due_memory_review_nudges_require_reasons_and_receipts() -> None:
    with pytest.raises(ValidationError, match="reasons"):
        MemoryReviewNudge(
            id="memory_review_invalid",
            candidate_ref="fact_memory_policy",
            status="due",
            receipt_ids=["receipt_memory_review"],
        )

    with pytest.raises(ValidationError, match="receipt_ids"):
        memory_review_nudge(
            nudge_id="memory_review_stale",
            candidate=_candidate(last_reviewed_at=datetime(2026, 5, 1, 21, 15, tzinfo=UTC)),
            now=NOW,
            review_interval_days=7,
            receipt_ids=[],
        )


def test_not_due_memory_review_nudges_do_not_carry_reasons() -> None:
    with pytest.raises(ValidationError, match="must not include reasons"):
        MemoryReviewNudge(
            id="memory_review_invalid",
            candidate_ref="fact_memory_policy",
            status="not_due",
            reasons=["stale"],
        )
