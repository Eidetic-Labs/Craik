"""Execution helpers for the governed single-agent loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from craik.contracts.models import (
    CapabilityGrant,
    CapabilityReceipt,
    IntentLock,
    PolicyEnvelope,
    ReceiptResult,
    RunnerStepResult,
    TaskRunPhase,
)
from craik.runtime.auth.operator import active_operator_session
from craik.runtime.policy.credential_policy import credential_policy_metadata
from craik.runtime.policy.operator_policy import check_operator_policy
from craik.runtime.policy.policy import (
    GrantDecision,
    check_shell_grant,
    denial_receipt,
)
from craik.runtime.work.run_outputs import RunOutputProposalSpec


@dataclass(frozen=True)
class LoopStep:
    """One planned loop phase."""

    phase: TaskRunPhase
    input_prompt: str
    context: dict[str, object] = field(default_factory=dict)
    side_effect_capability: str | None = None
    side_effect_target: str | None = None
    proposal_specs: list[RunOutputProposalSpec] = field(default_factory=list)


def default_loop_steps() -> list[LoopStep]:
    """Return the default deterministic single-agent loop phases."""
    return [
        LoopStep(phase="plan", input_prompt="Plan the next governed step."),
        LoopStep(
            phase="act",
            input_prompt="Perform the approved action.",
            side_effect_capability="shell.execute",
            side_effect_target="fixture-action",
        ),
        LoopStep(phase="observe", input_prompt="Capture observed output."),
        LoopStep(phase="evaluate", input_prompt="Evaluate whether the task is complete."),
    ]


def operator_policy_decision(policy: PolicyEnvelope) -> GrantDecision:
    """Evaluate operator policy against the active operator session."""
    session = active_operator_session()
    return check_operator_policy(
        policy=policy,
        operator_subject=session.subject if session is not None else None,
        operator_issuer=session.issuer if session is not None else None,
        operator_groups=list(session.groups) if session is not None else [],
    )


def runtime_policy_context(
    context: dict[str, object],
    *,
    operator_policy: dict[str, object],
    credential_policy: dict[str, object],
) -> dict[str, object]:
    """Return loop context augmented with runtime policy metadata."""
    updated = dict(context)
    policies = {"operator_policy": operator_policy, "credential_policy": credential_policy}
    for key, value in policies.items():
        if value:
            updated[key] = dict(value)
    return updated


def credential_policy_context(policy: PolicyEnvelope) -> dict[str, object]:
    """Return serializable credential policy metadata for provider calls."""
    return credential_policy_metadata(policy)


def intent_stop_reason(intent_lock: IntentLock | None, step: LoopStep) -> str | None:
    """Return the triggered intent stop reason for a step, if any."""
    if intent_lock is None:
        return None
    trigger = step.context.get("trigger_stop_condition")
    if trigger is None:
        return None
    if str(trigger) in intent_lock.stop_conditions:
        return f"intent stop condition triggered: {trigger}"
    return None


def time_budget_stop_reason(
    *,
    started_at: datetime,
    budget_seconds: float | None,
    now: datetime | None = None,
) -> str | None:
    """Return a stop reason when a run has exhausted its wall-clock budget."""
    if budget_seconds is None:
        return None
    checked_at = now or datetime.now(UTC)
    if checked_at >= started_at + timedelta(seconds=budget_seconds):
        return f"wall-clock budget {budget_seconds:g}s exceeded"
    return None


def provider_budget_stop_reason(remaining_tokens: int | None) -> str | None:
    """Return a stop reason when the provider token budget is exhausted."""
    if remaining_tokens == 0:
        return "provider token budget exhausted"
    return None


def provider_usage_total_tokens(observed_output: dict[str, object]) -> int:
    """Extract normalized provider token usage from a runner observed output."""
    usage = observed_output.get("usage")
    if not isinstance(usage, dict):
        return 0
    raw_total = usage.get("total_tokens", usage.get("total", 0))
    if isinstance(raw_total, bool):
        return 0
    if isinstance(raw_total, int):
        return max(raw_total, 0)
    return 0


def request_id(run_id: str, index: int, phase: TaskRunPhase, tool_round: int) -> str:
    """Return the stable request id for a loop step/tool round."""
    base = f"runner_step_request_{run_id}_{index}_{phase}"
    if tool_round == 0:
        return base
    return f"{base}_tool_round_{tool_round}"


def loop_step_key(run_id: str, index: int, phase: TaskRunPhase) -> str:
    """Return the stable idempotency key for one run phase boundary."""
    return f"{run_id}:{index}:{phase}"


def message_history_from_context(context: dict[str, object]) -> list[dict[str, str]]:
    """Extract normalized message history from step context."""
    raw_messages = context.get("message_history") or context.get("messages")
    if not isinstance(raw_messages, list):
        return []
    messages: list[dict[str, str]] = []
    for raw_message in raw_messages:
        if not isinstance(raw_message, dict):
            continue
        role = raw_message.get("role")
        content = raw_message.get("content")
        if role is None or content is None:
            continue
        message = {"role": str(role), "content": str(content)}
        tool_call_id = raw_message.get("tool_call_id")
        if tool_call_id is not None:
            message["tool_call_id"] = str(tool_call_id)
        messages.append(message)
    return messages


def context_with_message_history(
    context: dict[str, object],
    message_history: list[dict[str, str]],
) -> dict[str, object]:
    """Return context with message history attached when present."""
    if not message_history:
        return dict(context)
    return {**context, "message_history": list(message_history)}


def context_with_idempotency(
    context: dict[str, object],
    *,
    step_key: str,
    tool_round: int,
) -> dict[str, object]:
    """Return context with replay-safe idempotency metadata."""
    return {
        **context,
        "idempotency_key": step_key,
        "tool_round": tool_round,
    }


def result_with_idempotency_key(
    result: RunnerStepResult,
    step_key: str,
) -> RunnerStepResult:
    """Record the phase idempotency key on captured observed output."""
    observed_output = dict(result.observed_output)
    observed_output.setdefault("idempotency_key", step_key)
    return result.model_copy(update={"observed_output": observed_output})


def stream_chunks_from_output(observed_output: dict[str, object]) -> list[str]:
    """Return replayable streaming chunks from persisted observed output."""
    chunks = observed_output.get("stream_chunks")
    if not isinstance(chunks, list):
        return []
    return [chunk for chunk in chunks if isinstance(chunk, str)]


def side_effect_receipt(
    *,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    step: LoopStep,
    actor: str,
) -> CapabilityReceipt | None:
    """Return a step-level side-effect receipt, or None when no side effect exists."""
    if step.side_effect_capability is None:
        return None
    target = step.side_effect_target or step.phase
    if step.side_effect_capability != "shell.execute":
        decision = check_shell_grant(policy=policy, grants=[], command=target)
    else:
        decision = check_shell_grant(policy=policy, grants=grants, command=target)
    if not decision.allowed:
        return denial_receipt(policy=policy, decision=decision, actor=actor)
    return CapabilityReceipt(
        id=f"receipt_{policy.task_id}_{step.phase}_{_receipt_slug(target)}",
        task_id=policy.task_id,
        actor=actor,
        capability=decision.capability,
        target=target,
        policy_profile=policy.profile,
        fail_open=policy.fail_open,
        reason=decision.reason,
        result=ReceiptResult(status="passed", summary=decision.reason),
        redacted=True,
        created_at=datetime.now(UTC),
    )


def _receipt_slug(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")
