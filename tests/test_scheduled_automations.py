from datetime import UTC, datetime

from craik.contracts.models import PolicyEnvelope
from craik.runtime.scheduled_automations import (
    ScheduledAutomation,
    run_scheduled_automation_tick,
    scheduled_automation_receipt,
)
from craik.runtime.schedules import GatewaySchedule

NOW = datetime(2026, 5, 16, 19, 35, tzinfo=UTC)


def _schedule() -> GatewaySchedule:
    return GatewaySchedule(
        id="daily_status",
        project_id="project_craik",
        title="Daily gateway status",
        objective="Summarize gateway health and open risks.",
        cron="0 9 * * *",
        channel="scheduler",
    )


def _automation(enabled: bool = True) -> ScheduledAutomation:
    return ScheduledAutomation(
        id="automation_daily_status",
        schedule=_schedule(),
        enabled=enabled,
        policy_envelope_id="policy_schedule",
        receipt_ids=["receipt_schedule_trigger"],
    )


def _policy(*, allowed: bool = True) -> PolicyEnvelope:
    return PolicyEnvelope(
        id="policy_schedule",
        task_id="task_gateway",
        actor="gateway:scheduler",
        profile="strict",
        fail_open=False,
        allowed_capabilities=["gateway.schedule.execute"] if allowed else [],
        denied_capabilities=[] if allowed else ["gateway.schedule.execute"],
        approval_required=[],
        verification_required=["schedule.enabled", "policy.envelope"],
        handoff_required=True,
        receipt_required=True,
        redaction_required=True,
    )


def test_enabled_scheduled_automation_creates_task() -> None:
    result = run_scheduled_automation_tick(
        automation=_automation(enabled=True),
        policy=_policy(),
        tick_id="2026-05-16T09:00:00Z",
        run_at=NOW,
        seen_tick_ids=set(),
    )

    assert result.status == "created"
    assert result.task_creation is not None
    assert result.task_creation.task is not None
    assert result.task_creation.task.project_id == "project_craik"
    assert "policy_envelope_id=policy_schedule" in result.task_creation.task.constraints
    assert "receipt_id=receipt_schedule_trigger" in result.task_creation.task.constraints


def test_disabled_scheduled_automation_does_not_create_task() -> None:
    result = run_scheduled_automation_tick(
        automation=_automation(enabled=False),
        policy=_policy(),
        tick_id="2026-05-16T09:00:00Z",
        run_at=NOW,
        seen_tick_ids=set(),
    )

    assert result.status == "disabled"
    assert result.task_creation is None


def test_policy_denied_scheduled_automation_does_not_create_task() -> None:
    result = run_scheduled_automation_tick(
        automation=_automation(enabled=True),
        policy=_policy(allowed=False),
        tick_id="2026-05-16T09:00:00Z",
        run_at=NOW,
        seen_tick_ids=set(),
    )

    assert result.status == "policy_denied"
    assert result.reason == "policy does not allow gateway.schedule.execute"
    assert result.task_creation is None


def test_scheduled_automation_deduplicates_seen_tick() -> None:
    result = run_scheduled_automation_tick(
        automation=_automation(enabled=True),
        policy=_policy(),
        tick_id="2026-05-16T09:00:00Z",
        run_at=NOW,
        seen_tick_ids={"2026-05-16T09:00:00Z"},
    )

    assert result.status == "duplicate"
    assert result.task_creation is not None
    assert result.task_creation.task is None


def test_scheduled_automation_receipt_links_task_when_created() -> None:
    result = run_scheduled_automation_tick(
        automation=_automation(enabled=True),
        policy=_policy(),
        tick_id="2026-05-16T09:00:00Z",
        run_at=NOW,
        seen_tick_ids=set(),
    )

    receipt = scheduled_automation_receipt(result=result, policy=_policy(), created_at=NOW)

    assert receipt.result.status == "passed"
    assert receipt.capability == "gateway.schedule.execute"
    assert receipt.result.metadata["automation_id"] == "automation_daily_status"
    assert receipt.result.metadata["task_id"] == "task_schedule_daily_status_2026_05_16t09_00_00z"
