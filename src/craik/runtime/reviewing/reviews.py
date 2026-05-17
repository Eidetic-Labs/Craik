"""Cross-agent review and adjudication helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.contracts.models import (
    AdjudicatedFinding,
    AdjudicationDecision,
    AdjudicationOutcome,
    ReviewRequest,
    ReviewResult,
)
from craik.runtime.store import LocalStore


class ReviewAdjudicationManager:
    """Persist cross-agent reviews and deterministic adjudication outcomes."""

    def __init__(self, store: LocalStore) -> None:
        self._store = store

    def request_review(self, request: ReviewRequest) -> ReviewRequest:
        """Persist a bounded specialist review request."""
        self._store.put_review_request(request)
        return request

    def record_result(self, result: ReviewResult) -> ReviewResult:
        """Persist a specialist review result and mark its request complete."""
        self._store.put_review_result(result)
        request = self._store.get_review_request(result.review_request_id)
        if request is not None and request.status == "open":
            self._store.put_review_request(request.model_copy(update={"status": "completed"}))
        return result

    def adjudicate(
        self,
        *,
        task_id: str,
        outcome_id: str,
        adjudicator_role_id: str,
        decision: AdjudicationDecision,
        summary: str,
        review_results: list[ReviewResult],
        findings: list[AdjudicatedFinding],
        debate_summary_ids: list[str] | None = None,
        unresolved_disagreements: list[str] | None = None,
        contradiction_ids: list[str] | None = None,
        receipt_ids: list[str] | None = None,
        handoff_ids: list[str] | None = None,
    ) -> AdjudicationOutcome:
        """Persist a deterministic adjudicator outcome over review results."""
        for result in review_results:
            self.record_result(result)
        linked_contradiction_ids = {
            contradiction_id
            for result in review_results
            for contradiction_id in result.contradiction_ids
        }
        linked_receipt_ids = {
            receipt_id for result in review_results for receipt_id in result.receipt_ids
        }
        linked_handoff_ids = {
            result.handoff_id for result in review_results if result.handoff_id
        }
        outcome = AdjudicationOutcome(
            id=outcome_id,
            task_id=task_id,
            adjudicator_role_id=adjudicator_role_id,
            decision=decision,
            summary=summary,
            review_result_ids=sorted(result.id for result in review_results),
            worker_result_ids=sorted(
                {worker_id for result in review_results for worker_id in result.worker_result_ids}
            ),
            debate_summary_ids=sorted(debate_summary_ids or []),
            adjudicated_findings=sorted(
                findings,
                key=lambda finding: (
                    finding.source_worker_result_id or "",
                    finding.source_finding_id or "",
                    finding.source_review_result_id or "",
                    finding.decision,
                ),
            ),
            unresolved_disagreements=sorted(unresolved_disagreements or []),
            contradiction_ids=sorted({*linked_contradiction_ids, *(contradiction_ids or [])}),
            receipt_ids=sorted({*linked_receipt_ids, *(receipt_ids or [])}),
            handoff_ids=sorted({*linked_handoff_ids, *(handoff_ids or [])}),
            policy_review_result_ids=sorted(
                result.id
                for result in review_results
                if result.reviewer_role_kind == "policy_reviewer"
            ),
            adversarial_review_result_ids=sorted(
                result.id
                for result in review_results
                if result.reviewer_role_kind == "adversarial_reviewer"
            ),
            created_at=datetime.now(UTC),
        )
        self._store.put_adjudication_outcome(outcome)
        return outcome
