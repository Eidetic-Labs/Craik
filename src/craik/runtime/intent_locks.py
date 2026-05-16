"""Task intent lock helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.contracts.models import IntentLock, TaskRequest
from craik.runtime.store import LocalStore

DEFAULT_ALLOWED_AUTONOMY = (
    "Inspect local repository state.",
    "Build deterministic case context.",
    "Report missing context as assumptions.",
)
DEFAULT_STOP_CONDITIONS = (
    "The requested work conflicts with policy or immutable path rules.",
    "Required project context is missing.",
    "The task objective changes materially.",
)
DEFAULT_SCOPE_CHANGE_RULES = (
    "Do not expand scope without an updated intent lock.",
    "Record excluded work as out of scope instead of silently performing it.",
)


class IntentLockError(RuntimeError):
    """Base error for intent lock failures."""


class IntentLockNotFoundError(IntentLockError):
    """Raised when an intent lock cannot be found."""


class IntentLockManager:
    """Create and inspect task intent locks."""

    def __init__(self, store: LocalStore) -> None:
        self._store = store

    def create_for_task(
        self,
        task: TaskRequest,
        *,
        accepted_interpretation: str | None = None,
        in_scope: list[str] | None = None,
        out_of_scope: list[str] | None = None,
        allowed_autonomy: list[str] | None = None,
        stop_conditions: list[str] | None = None,
        scope_change_rules: list[str] | None = None,
    ) -> IntentLock:
        """Create and persist an intent lock for a task."""
        intent_lock = IntentLock(
            id=intent_lock_id(task.id),
            task_id=task.id,
            original_request=task.title,
            objective=task.objective,
            accepted_interpretation=accepted_interpretation or task.objective,
            in_scope=in_scope or list(task.expected_outputs),
            out_of_scope=out_of_scope or list(task.constraints),
            allowed_autonomy=allowed_autonomy or list(DEFAULT_ALLOWED_AUTONOMY),
            stop_conditions=stop_conditions or list(DEFAULT_STOP_CONDITIONS),
            scope_change_rules=scope_change_rules or list(DEFAULT_SCOPE_CHANGE_RULES),
            created_at=datetime.now(UTC),
        )
        self._store.put_intent_lock(intent_lock)
        return intent_lock

    def ensure_for_task(self, task: TaskRequest) -> IntentLock:
        """Return the existing task intent lock or create a default one."""
        existing = self._store.get_intent_lock(intent_lock_id(task.id))
        if existing is not None:
            return existing
        return self.create_for_task(task)

    def get(self, intent_lock_id_or_task_id: str) -> IntentLock | None:
        """Load an intent lock by lock id or task id."""
        intent_lock = self._store.get_intent_lock(intent_lock_id_or_task_id)
        if intent_lock is not None:
            return intent_lock
        return self._store.get_intent_lock(intent_lock_id(intent_lock_id_or_task_id))

    def require(self, intent_lock_id_or_task_id: str) -> IntentLock:
        """Load an intent lock or raise a clear error."""
        intent_lock = self.get(intent_lock_id_or_task_id)
        if intent_lock is None:
            message = f"unknown intent lock or task: {intent_lock_id_or_task_id}"
            raise IntentLockNotFoundError(message)
        return intent_lock


def intent_lock_id(task_id: str) -> str:
    """Return the stable intent lock id for a task id."""
    return f"intent_{task_id.removeprefix('task_')}"
