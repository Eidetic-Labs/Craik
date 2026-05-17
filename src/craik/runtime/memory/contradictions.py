"""Local contradiction report lifecycle."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from craik.contracts.models import ContradictionReport, ContradictionStatus, EvidenceReference
from craik.runtime.policy.redaction import redact
from craik.runtime.store import LocalStore


class ContradictionError(RuntimeError):
    """Base error for contradiction report failures."""


class ContradictionNotFoundError(ContradictionError):
    """Raised when a contradiction report cannot be found."""


class ContradictionManager:
    """Manage local contradiction reports."""

    def __init__(self, store: LocalStore) -> None:
        self._store = store

    def open_report(
        self,
        *,
        task_id: str | None,
        facts: list[str],
        summary: str,
        affected_artifacts: list[str],
        evidence_ids: list[str],
        owner: str | None = None,
        proposed_resolution: str | None = None,
        stigmem_conflict_id: str | None = None,
    ) -> ContradictionReport:
        """Create and persist a local contradiction report."""
        redacted_summary = str(redact(summary).value)
        report = ContradictionReport(
            id=contradiction_id(task_id=task_id, summary=redacted_summary),
            task_id=task_id,
            facts=[str(redact(fact).value) for fact in facts],
            summary=redacted_summary,
            affected_artifacts=[str(redact(path).value) for path in affected_artifacts],
            evidence_ids=[str(redact(evidence_id).value) for evidence_id in evidence_ids],
            proposed_resolution=(
                str(redact(proposed_resolution).value) if proposed_resolution else None
            ),
            status="open",
            owner=str(redact(owner).value) if owner else None,
            stigmem_conflict_id=(
                str(redact(stigmem_conflict_id).value) if stigmem_conflict_id else None
            ),
            created_at=datetime.now(UTC),
        )
        self._store.put_contradiction(report)
        return report

    def list_reports(
        self,
        *,
        task_id: str | None = None,
        status: ContradictionStatus | None = None,
    ) -> list[ContradictionReport]:
        """List contradiction reports with optional filters."""
        reports = self._store.list_contradictions()
        if task_id is not None:
            reports = [report for report in reports if report.task_id == task_id]
        if status is not None:
            reports = [report for report in reports if report.status == status]
        return sorted(reports, key=lambda report: report.id)

    def get_report(self, report_id: str) -> ContradictionReport:
        """Load one contradiction report."""
        report = self._store.get_contradiction(report_id)
        if report is None:
            raise ContradictionNotFoundError(f"unknown contradiction: {report_id}")
        return report

    def evidence_for(self, report_id: str) -> list[EvidenceReference]:
        """Return evidence linked to one contradiction report."""
        report = self.get_report(report_id)
        evidence = []
        for evidence_id in report.evidence_ids:
            item = self._store.get_evidence(evidence_id)
            if item is not None:
                evidence.append(item)
        return sorted(evidence, key=lambda item: item.id)


def contradiction_id(*, task_id: str | None, summary: str) -> str:
    """Create a stable contradiction id."""
    prefix = task_id or "global"
    return f"contradiction_{_slug(prefix)}_{_slug(summary)[:48]}"


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "value"
