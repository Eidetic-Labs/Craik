"""Known trap and negative knowledge helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.contracts.models import KnownTrap, NegativeKnowledge
from craik.runtime.store import LocalStore


def active_known_traps(
    store: LocalStore,
    project_id: str,
    *,
    now: datetime | None = None,
) -> list[KnownTrap]:
    """Return active, unexpired, uncontradicted traps for a project."""
    current = now or datetime.now(UTC)
    return sorted(
        (
            trap
            for trap in store.list_known_traps()
            if trap.status == "active"
            and (trap.project_id is None or trap.project_id == project_id)
            and (trap.expires_at is None or trap.expires_at > current)
        ),
        key=lambda trap: trap.id,
    )


def known_trap_summaries(
    store: LocalStore,
    project_id: str,
    *,
    now: datetime | None = None,
) -> list[str]:
    """Return deterministic onboarding/case-file summaries for active traps."""
    return [
        f"{trap.statement} Avoidance: {trap.avoidance}"
        for trap in active_known_traps(store, project_id, now=now)
    ]


def active_negative_knowledge(
    store: LocalStore,
    project_id: str,
    *,
    now: datetime | None = None,
) -> list[NegativeKnowledge]:
    """Return unexpired negative knowledge for a project."""
    current = now or datetime.now(UTC)
    return sorted(
        (
            knowledge
            for knowledge in store.list_negative_knowledge()
            if (knowledge.project_id is None or knowledge.project_id == project_id)
            and (knowledge.expires_at is None or knowledge.expires_at > current)
            and not knowledge.contradiction_ids
        ),
        key=lambda knowledge: knowledge.id,
    )
