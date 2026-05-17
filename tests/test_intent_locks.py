from pathlib import Path

import pytest

from craik.runtime.paths import ensure_craik_home
from craik.runtime.policy.intent_locks import IntentLockManager, IntentLockNotFoundError
from craik.runtime.store import LocalStore
from craik.runtime.work.tasks import create_task


@pytest.fixture
def store(tmp_path: Path):
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_create_intent_lock_captures_scope_controls(store: LocalStore) -> None:
    task = create_task(
        store,
        title="Review docs",
        objective="Review docs against implementation.",
        project_id="project_example",
        constraints=["Do not edit ADRs."],
        expected_outputs=["case_file", "findings"],
    )

    intent_lock = IntentLockManager(store).create_for_task(
        task,
        accepted_interpretation="Review docs only.",
        in_scope=["README.md", "docs/"],
        out_of_scope=["docs/adr/"],
        allowed_autonomy=["Read repository files."],
        stop_conditions=["A requested change touches ADRs."],
        scope_change_rules=["Ask before changing code."],
    )

    assert intent_lock.id == "intent_review_docs"
    assert intent_lock.original_request == "Review docs"
    assert intent_lock.accepted_interpretation == "Review docs only."
    assert intent_lock.in_scope == ["README.md", "docs/"]
    assert intent_lock.out_of_scope == ["docs/adr/"]
    assert intent_lock.allowed_autonomy == ["Read repository files."]
    assert intent_lock.stop_conditions == ["A requested change touches ADRs."]
    assert intent_lock.scope_change_rules == ["Ask before changing code."]
    assert store.get_intent_lock(intent_lock.id) == intent_lock


def test_ensure_for_task_reuses_existing_intent_lock(store: LocalStore) -> None:
    task = create_task(
        store,
        title="Build case",
        objective="Build case file.",
        project_id="project_example",
    )
    manager = IntentLockManager(store)

    created = manager.create_for_task(task, accepted_interpretation="Build the case file.")
    ensured = manager.ensure_for_task(task)

    assert ensured == created


def test_get_and_require_accept_task_or_intent_id(store: LocalStore) -> None:
    task = create_task(
        store,
        title="Inspect scope",
        objective="Inspect scope controls.",
        project_id="project_example",
    )
    manager = IntentLockManager(store)
    created = manager.create_for_task(task)

    assert manager.get(task.id) == created
    assert manager.get(created.id) == created
    with pytest.raises(IntentLockNotFoundError, match="unknown intent lock or task"):
        manager.require("task_missing")
