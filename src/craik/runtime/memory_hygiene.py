"""Memory hygiene checks for MVP case-file readiness."""

from __future__ import annotations

from dataclasses import dataclass, field

from craik.runtime.store import LocalStore


@dataclass(frozen=True)
class MemoryHygieneReport:
    """Summary of local memory state that may affect continuity."""

    task_id: str | None = None
    pending_proposals: list[str] = field(default_factory=list)
    approved_proposals: list[str] = field(default_factory=list)
    open_contradictions: list[str] = field(default_factory=list)
    recent_handoffs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        return not self.warnings


def memory_hygiene_report(store: LocalStore, *, task_id: str | None = None) -> MemoryHygieneReport:
    """Return a deterministic hygiene report for memory-backed workflows."""
    proposals = [
        proposal
        for proposal in store.list_proposals()
        if task_id is None or proposal.task_id == task_id
    ]
    contradictions = [
        report
        for report in store.list_contradictions()
        if report.status == "open" and (task_id is None or report.task_id == task_id)
    ]
    handoffs = [
        handoff
        for handoff in store.list_handoffs()
        if task_id is None or handoff.task_id == task_id
    ]
    pending = sorted(proposal.id for proposal in proposals if proposal.status == "pending")
    approved = sorted(proposal.id for proposal in proposals if proposal.status == "approved")
    open_ids = sorted(report.id for report in contradictions)
    recent = [
        handoff.id
        for handoff in sorted(handoffs, key=lambda item: item.created_at, reverse=True)[:5]
    ]
    warnings: list[str] = []
    if pending:
        warnings.append("pending memory proposals require review before release")
    if open_ids:
        warnings.append("open contradictions should be resolved or carried into case files")
    if task_id and not recent:
        warnings.append("no recent handoff is available for this task")
    return MemoryHygieneReport(
        task_id=task_id,
        pending_proposals=pending,
        approved_proposals=approved,
        open_contradictions=open_ids,
        recent_handoffs=recent,
        warnings=warnings,
    )
