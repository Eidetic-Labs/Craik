"""Context request and exit discipline helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from craik.contracts.models import (
    ContextRequest,
    ExitDisciplineCheck,
    ExitDisciplineStatus,
    Handoff,
)


def build_exit_discipline_check(
    handoff: Handoff | None,
    *,
    task_id: str,
    project_id: str | None = None,
    context_requests: list[ContextRequest] | None = None,
    unknown_ids: list[str] | None = None,
    created_at: datetime | None = None,
) -> ExitDisciplineCheck:
    """Build an exit discipline check from a handoff and unresolved context."""
    requests = context_requests or []
    blockers: list[str] = []
    validation_recorded = bool(handoff and handoff.self_audit.validation_recorded)
    handoff_recorded = handoff is not None
    residual_risks_recorded = bool(handoff and (handoff.risks or handoff.status == "completed"))
    next_steps_recorded = bool(handoff and handoff.next_steps)
    if not validation_recorded:
        blockers.append("Validation was not recorded.")
    if not handoff_recorded:
        blockers.append("No handoff was recorded.")
    if not residual_risks_recorded:
        blockers.append("Residual risks were not recorded.")
    if not next_steps_recorded:
        blockers.append("Next steps were not recorded.")
    if any(request.status == "open" for request in requests):
        blockers.append("Open context requests remain.")
    status = cast(ExitDisciplineStatus, "blocked" if blockers else "complete")
    return ExitDisciplineCheck(
        id=f"exit_discipline_{task_id}",
        task_id=task_id,
        project_id=project_id or (handoff.project_id if handoff else None),
        handoff_id=handoff.id if handoff else None,
        status=status,
        validation_recorded=validation_recorded,
        handoff_recorded=handoff_recorded,
        residual_risks_recorded=residual_risks_recorded,
        next_steps_recorded=next_steps_recorded,
        blocking_reasons=blockers,
        context_request_ids=[request.id for request in requests],
        unknown_ids=unknown_ids or [],
        created_at=created_at or datetime.now(UTC),
    )
