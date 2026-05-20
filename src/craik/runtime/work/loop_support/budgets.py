"""Budget interruption helpers for the governed execution loop."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.runtime.work.loop_support.execution import (
    provider_budget_stop_reason,
    time_budget_stop_reason,
)
from craik.runtime.work.runs import RunTransition, TaskRunManager


def raise_time_budget_if_exhausted(
    *,
    runs: TaskRunManager,
    run_id: str,
    iteration: int,
    error_type: type[RuntimeError],
) -> None:
    """Interrupt the run when its wall-clock budget is exhausted."""
    run = runs.require(run_id)
    stop_reason = time_budget_stop_reason(
        started_at=run.started_at,
        budget_seconds=run.wall_clock_budget_seconds,
    )
    if stop_reason is not None:
        _interrupt_for_budget(runs, run.id, iteration, stop_reason, error_type)


def raise_provider_budget_if_exhausted(
    *,
    runs: TaskRunManager,
    run_id: str,
    iteration: int,
    error_type: type[RuntimeError],
) -> None:
    """Interrupt the run when its provider token budget is exhausted."""
    run = runs.require(run_id)
    stop_reason = provider_budget_stop_reason(run.provider_token_budget_remaining)
    if stop_reason is not None:
        _interrupt_for_budget(runs, run.id, iteration, stop_reason, error_type)


def _interrupt_for_budget(
    runs: TaskRunManager,
    run_id: str,
    iteration: int,
    stop_reason: str,
    error_type: type[RuntimeError],
) -> None:
    run = runs.transition(
        run_id,
        RunTransition(
            status="interrupted",
            phase="stop",
            iteration=iteration,
            stop_reason=stop_reason,
            at=datetime.now(UTC),
        ),
    )
    raise error_type(run.stop_reason or stop_reason)
