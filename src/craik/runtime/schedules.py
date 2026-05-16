"""Cron-like gateway schedule task creation."""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import Field

from craik.contracts.models import CraikModel, Priority, TaskMode, TaskRequest


class GatewaySchedule(CraikModel):
    """Cron-like schedule definition for gateway-created tasks."""

    id: str
    project_id: str
    title: str
    objective: str
    cron: str
    requested_by: str = "gateway:scheduler"
    priority: Priority = "normal"
    mode: TaskMode = "implement"
    policy_envelope_id: str | None = None
    channel: str | None = None
    receipt_ids: list[str] = Field(default_factory=list)


class ScheduledTaskCreation(CraikModel):
    """Result of converting one schedule tick into a task request."""

    created: bool
    reason: str
    schedule_id: str
    tick_id: str
    task: TaskRequest | None = None


def create_task_from_schedule_tick(
    *,
    schedule: GatewaySchedule,
    tick_id: str,
    run_at: datetime,
    seen_tick_ids: set[str],
) -> ScheduledTaskCreation:
    """Create one deterministic task for a schedule tick unless already seen."""
    validate_cron_expression(schedule.cron)
    if tick_id in seen_tick_ids:
        return ScheduledTaskCreation(
            created=False,
            reason="schedule tick already created a task",
            schedule_id=schedule.id,
            tick_id=tick_id,
        )
    constraints = [
        f"schedule_id={schedule.id}",
        f"schedule_tick_id={tick_id}",
        f"schedule_cron={schedule.cron}",
        f"schedule_run_at={run_at.isoformat()}",
    ]
    if schedule.policy_envelope_id:
        constraints.append(f"policy_envelope_id={schedule.policy_envelope_id}")
    if schedule.channel:
        constraints.append(f"channel={schedule.channel}")
    constraints.extend(f"receipt_id={receipt_id}" for receipt_id in schedule.receipt_ids)
    task = TaskRequest(
        id=f"task_schedule_{_slug(schedule.id)}_{_slug(tick_id)}",
        title=schedule.title,
        objective=schedule.objective,
        project_id=schedule.project_id,
        requested_by=schedule.requested_by,
        priority=schedule.priority,
        mode=schedule.mode,
        constraints=constraints,
        expected_outputs=["case_file", "handoff", "receipt"],
        created_at=run_at,
    )
    return ScheduledTaskCreation(
        created=True,
        reason="schedule tick created task",
        schedule_id=schedule.id,
        tick_id=tick_id,
        task=task,
    )


def validate_cron_expression(expression: str) -> None:
    """Validate a conservative five-field cron-like expression."""
    fields = expression.split()
    if len(fields) != 5:
        raise ValueError("cron-like schedule requires five fields")
    for field in fields:
        if not re.fullmatch(r"[\d*/,\-]+", field):
            raise ValueError(f"unsupported cron field: {field}")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "unknown"
