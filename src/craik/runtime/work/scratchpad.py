"""Expiring scratchpad and first-class unknown helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.contracts.models import ScratchpadRecord, UnknownRecord
from craik.runtime.store import LocalStore


def active_scratchpad_records(
    store: LocalStore,
    task_id: str,
    *,
    now: datetime | None = None,
) -> list[ScratchpadRecord]:
    """Return active scratchpad entries that have not expired."""
    current = now or datetime.now(UTC)
    return sorted(
        (
            record
            for record in store.list_scratchpad_records()
            if record.task_id == task_id
            and record.status == "active"
            and record.expires_at > current
        ),
        key=lambda record: record.id,
    )


def unresolved_unknowns(store: LocalStore, task_id: str) -> list[UnknownRecord]:
    """Return unresolved unknowns for a task."""
    return sorted(
        (
            record
            for record in store.list_unknown_records()
            if record.task_id == task_id and record.status == "unresolved"
        ),
        key=lambda record: record.id,
    )


def unknown_summaries(store: LocalStore, task_id: str) -> list[str]:
    """Return deterministic summaries for handoffs and case-file stale risks."""
    return [
        f"Unknown unresolved: {record.question} Next action: {record.next_action}"
        for record in unresolved_unknowns(store, task_id)
    ]
