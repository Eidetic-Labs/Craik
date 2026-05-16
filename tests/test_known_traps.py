from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from craik.contracts.models import KnownTrap, NegativeKnowledge
from craik.runtime.known_traps import active_known_traps, active_negative_knowledge
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore

NOW = datetime(2026, 5, 16, 9, 40, tzinfo=UTC)


def _store(tmp_path) -> LocalStore:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    return store


def _trap(**overrides: object) -> KnownTrap:
    payload = {
        "id": "trap_stale_github",
        "project_id": "project_traps",
        "kind": "tool",
        "status": "active",
        "statement": "GitHub state can become stale during a run.",
        "avoidance": "Refresh issue and PR state before acting on it.",
        "evidence_ids": ["evidence_trap"],
        "created_at": NOW,
    }
    payload.update(overrides)
    return KnownTrap.model_validate(payload)


def _negative(**overrides: object) -> NegativeKnowledge:
    payload = {
        "id": "negative_no_ui",
        "project_id": "project_traps",
        "statement": "No UI implementation exists in this repo.",
        "scope": "repository",
        "trust_class": "observed",
        "evidence_ids": ["evidence_tree"],
        "created_at": NOW,
        "expires_at": NOW + timedelta(days=1),
    }
    payload.update(overrides)
    return NegativeKnowledge.model_validate(payload)


def test_active_expired_and_contradicted_traps(tmp_path) -> None:
    store = _store(tmp_path)
    try:
        active = _trap()
        expired = _trap(
            id="trap_expired",
            created_at=NOW - timedelta(hours=2),
            expires_at=NOW - timedelta(minutes=1),
        )
        contradicted = _trap(
            id="trap_contradicted",
            status="contradicted",
            contradiction_ids=["contradiction_trap"],
        )
        store.put_known_trap(active)
        store.put_known_trap(expired)
        store.put_known_trap(contradicted)

        assert active_known_traps(store, "project_traps", now=NOW) == [active]
    finally:
        store.close()


def test_active_negative_knowledge_filters_expired_and_contradicted(tmp_path) -> None:
    store = _store(tmp_path)
    try:
        active = _negative()
        expired = _negative(
            id="negative_expired",
            created_at=NOW - timedelta(hours=2),
            expires_at=NOW - timedelta(minutes=1),
        )
        contradicted = _negative(
            id="negative_contradicted",
            contradiction_ids=["contradiction_negative"],
        )
        store.put_negative_knowledge(active)
        store.put_negative_knowledge(expired)
        store.put_negative_knowledge(contradicted)

        assert active_negative_knowledge(store, "project_traps", now=NOW) == [active]
    finally:
        store.close()


def test_active_known_trap_requires_evidence() -> None:
    with pytest.raises(ValidationError, match="active known traps require"):
        _trap(evidence_ids=[])


def test_negative_knowledge_requires_evidence() -> None:
    with pytest.raises(ValidationError, match="negative knowledge requires"):
        _negative(evidence_ids=[])
