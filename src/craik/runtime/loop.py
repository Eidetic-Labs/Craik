"""Governed single-agent execution loop."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol

from craik.contracts.models import (
    CapabilityGrant,
    CapabilityReceipt,
    IntentLock,
    PolicyEnvelope,
    ReceiptResult,
    RunnerMetadata,
    RunnerResultStatus,
    RunnerStepRequest,
    RunnerStepResult,
    TaskRun,
    TaskRunPhase,
    TaskRunStatus,
)
from craik.runtime.memory import MemoryStore
from craik.runtime.policy import check_shell_grant, denial_receipt
from craik.runtime.run_outputs import (
    RunOutputCapture,
    RunOutputProposalSpec,
    RunOutputRecorder,
)
from craik.runtime.runs import RunTransition, TaskRunManager
from craik.runtime.side_effects import (
    SideEffectResult,
    run_github_write,
    run_shell_command_ref,
)
from craik.runtime.store import LocalStore


class LoopExecutionError(RuntimeError):
    """Base error for governed loop execution failures."""


class LoopPolicyBlockedError(LoopExecutionError):
    """Raised when policy blocks a side-effect step."""


class LoopMaxIterationsError(LoopExecutionError):
    """Raised when the loop reaches its iteration bound."""


class RunnerStepHandler(Protocol):
    """Minimal runner boundary for one loop step."""

    def run_step(
        self,
        request: RunnerStepRequest,
        *,
        stream_callback: Callable[[str], None] | None = None,
    ) -> RunnerStepResult:
        """Execute one step request and return a normalized result."""


@dataclass(frozen=True)
class LoopStep:
    """One planned loop phase."""

    phase: TaskRunPhase
    input_prompt: str
    context: dict[str, object] = field(default_factory=dict)
    side_effect_capability: str | None = None
    side_effect_target: str | None = None
    proposal_specs: list[RunOutputProposalSpec] = field(default_factory=list)


@dataclass(frozen=True)
class LoopExecutionResult:
    """Summary of a completed or stopped loop execution."""

    run: TaskRun
    step_results: list[RunnerStepResult]
    output_captures: list[RunOutputCapture]
    receipts: list[CapabilityReceipt]


@dataclass
class FixtureStepRunner:
    """Deterministic step runner for local tests."""

    statuses: list[RunnerResultStatus] = field(default_factory=list)

    def run_step(
        self,
        request: RunnerStepRequest,
        *,
        stream_callback: Callable[[str], None] | None = None,
    ) -> RunnerStepResult:
        _ = stream_callback
        status = self.statuses.pop(0) if self.statuses else "completed"
        return RunnerStepResult(
            id=f"runner_step_result_{request.run_id}_{request.phase}_{request.id}",
            request_id=request.id,
            run_id=request.run_id,
            task_id=request.task_id,
            phase=request.phase,
            runner=request.runner,
            status=status,
            summary=f"Fixture {request.phase} step {status}.",
            observed_output={"phase": request.phase, "status": status},
            diagnostics=[] if status in {"completed", "partial"} else [f"fixture {status}"],
            created_at=datetime.now(UTC),
        )


class SingleAgentLoopExecutor:
    """Drive one agent through governed plan/act/observe/evaluate phases."""

    def __init__(
        self,
        *,
        store: LocalStore,
        memory: MemoryStore,
        runner: RunnerStepHandler,
    ) -> None:
        self.store = store
        self.memory = memory
        self.runner = runner
        self.runs = TaskRunManager(store)
        self.outputs = RunOutputRecorder(store, memory)

    def execute(
        self,
        *,
        task_id: str,
        case_file_id: str,
        policy: PolicyEnvelope,
        runner_metadata: RunnerMetadata,
        intent_lock: IntentLock | None = None,
        grants: list[CapabilityGrant] | None = None,
        steps: list[LoopStep] | None = None,
        max_iterations: int = 5,
        started_at: datetime | None = None,
    ) -> LoopExecutionResult:
        active_steps = steps or default_loop_steps()
        run = self.runs.create(
            task_id=task_id,
            case_file_id=case_file_id,
            policy_envelope_id=policy.id,
            intent_lock_id=intent_lock.id if intent_lock else None,
            runner_id=runner_metadata.id,
            runner_mode=runner_metadata.mode,
            max_iterations=max_iterations,
            created_at=started_at,
        )
        receipts: list[CapabilityReceipt] = []
        step_results: list[RunnerStepResult] = []
        output_captures: list[RunOutputCapture] = []
        active_grants = grants or []
        iteration = 0

        for index, step in enumerate(active_steps, start=1):
            if iteration >= max_iterations:
                run = self.runs.transition(
                    run.id,
                    RunTransition(
                        status="interrupted",
                        phase="stop",
                        stop_reason=f"max iterations {max_iterations} reached",
                        at=datetime.now(UTC),
                    ),
                )
                raise LoopMaxIterationsError(run.stop_reason or "max iterations reached")

            stop_reason = _intent_stop_reason(intent_lock, step)
            if stop_reason is not None:
                run = self.runs.transition(
                    run.id,
                    RunTransition(
                        status="blocked",
                        phase="stop",
                        iteration=index - 1,
                        stop_reason=stop_reason,
                        at=datetime.now(UTC),
                    ),
                )
                return LoopExecutionResult(run, step_results, output_captures, receipts)

            side_effect_receipt = self._side_effect_receipt(
                policy=policy,
                grants=active_grants,
                step=step,
                actor=f"runner:{runner_metadata.id}",
            )
            if side_effect_receipt is not None:
                self.store.put_receipt(side_effect_receipt)
                receipts.append(side_effect_receipt)
                if side_effect_receipt.result.status == "denied":
                    run = self.runs.transition(
                        run.id,
                        RunTransition(
                            status="blocked",
                            phase="stop",
                            iteration=index - 1,
                            receipt_id=side_effect_receipt.id,
                            stop_reason=side_effect_receipt.reason,
                            at=datetime.now(UTC),
                        ),
                    )
                    return LoopExecutionResult(run, step_results, output_captures, receipts)

            message_history = _message_history_from_context(step.context)
            tool_round = 0
            request = RunnerStepRequest(
                id="",
                run_id=run.id,
                task_id=task_id,
                phase=step.phase,
                runner=runner_metadata,
                policy_envelope_id=policy.id,
                intent_lock_id=intent_lock.id if intent_lock else None,
                capability_grant_ids=[grant.id for grant in active_grants],
                expected_output_schemas=["craik.runner_step_result"],
                input_prompt=step.input_prompt,
                context={},
                created_at=datetime.now(UTC),
            )
            while True:
                if iteration >= max_iterations:
                    run = self.runs.transition(
                        run.id,
                        RunTransition(
                            status="interrupted",
                            phase="stop",
                            stop_reason=f"max iterations {max_iterations} reached",
                            at=datetime.now(UTC),
                        ),
                    )
                    raise LoopMaxIterationsError(run.stop_reason or "max iterations reached")

                request = request.model_copy(
                    update={
                        "id": _request_id(run.id, index, step.phase, tool_round),
                        "context": _context_with_message_history(
                            step.context,
                            message_history,
                        ),
                        "created_at": datetime.now(UTC),
                    }
                )
                stream_chunks: list[str] = []
                result = self.runner.run_step(request, stream_callback=stream_chunks.append)
                iteration += 1
                if stream_chunks:
                    result = _result_with_stream_chunks(result, stream_chunks)
                receipt_ids = list(result.receipt_ids)
                if side_effect_receipt is not None and side_effect_receipt.id not in receipt_ids:
                    receipt_ids.append(side_effect_receipt.id)

                tool_calls = _dispatchable_tool_calls(result)
                tool_messages: list[dict[str, str]] = []
                denied_tool_receipt: CapabilityReceipt | None = None
                if tool_calls:
                    for tool_call in tool_calls:
                        side_effect = self._tool_call_side_effect(
                            policy=policy,
                            grants=active_grants,
                            tool_call=tool_call,
                            actor=f"runner:{runner_metadata.id}",
                        )
                        if side_effect is None:
                            continue
                        receipts.append(side_effect.receipt)
                        if side_effect.receipt.id not in receipt_ids:
                            receipt_ids.append(side_effect.receipt.id)
                        tool_messages.append(_tool_message(tool_call, side_effect))
                        if not side_effect.allowed:
                            denied_tool_receipt = side_effect.receipt
                            break

                if receipt_ids != result.receipt_ids:
                    result = result.model_copy(update={"receipt_ids": receipt_ids})
                capture = self.outputs.capture_step_result(
                    result,
                    proposal_specs=step.proposal_specs,
                )
                step_results.append(result)
                output_captures.append(capture)

                if denied_tool_receipt is not None:
                    run = self.runs.transition(
                        run.id,
                        RunTransition(
                            status="blocked",
                            phase="stop",
                            iteration=iteration,
                            receipt_id=denied_tool_receipt.id,
                            stop_reason=denied_tool_receipt.reason,
                            at=datetime.now(UTC),
                        ),
                    )
                    return LoopExecutionResult(run, step_results, output_captures, receipts)

                if result.status in {"blocked", "failed"}:
                    terminal_status: TaskRunStatus = (
                        "blocked" if result.status == "blocked" else "failed"
                    )
                    run = self.runs.transition(
                        run.id,
                        RunTransition(
                            status=terminal_status,
                            phase="stop",
                            iteration=iteration,
                            receipt_id=side_effect_receipt.id if side_effect_receipt else None,
                            stop_reason=result.summary,
                            at=datetime.now(UTC),
                        ),
                    )
                    return LoopExecutionResult(run, step_results, output_captures, receipts)

                if not tool_messages:
                    break
                message_history.extend(tool_messages)
                tool_round += 1

            run = self.runs.transition(
                run.id,
                RunTransition(
                    status="running",
                    phase=step.phase,
                    iteration=iteration,
                    receipt_id=side_effect_receipt.id if side_effect_receipt else None,
                    at=datetime.now(UTC),
                ),
            )

        run = self.runs.transition(
            run.id,
            RunTransition(
                status="completed",
                phase="stop",
                stop_reason="loop completed",
                at=datetime.now(UTC),
            ),
        )
        return LoopExecutionResult(run, step_results, output_captures, receipts)

    def _side_effect_receipt(
        self,
        *,
        policy: PolicyEnvelope,
        grants: list[CapabilityGrant],
        step: LoopStep,
        actor: str,
    ) -> CapabilityReceipt | None:
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

    def _tool_call_side_effect(
        self,
        *,
        policy: PolicyEnvelope,
        grants: list[CapabilityGrant],
        tool_call: dict[str, Any],
        actor: str,
    ) -> SideEffectResult | None:
        name = _tool_name(tool_call)
        arguments = _tool_arguments(tool_call)
        if name in {"shell.execute", "shell_execute", "run_shell_command_ref"}:
            command_ref = str(
                arguments.get("command_ref")
                or arguments.get("command")
                or arguments.get("target")
                or ""
            )
            return run_shell_command_ref(
                store=self.store,
                policy=policy,
                grants=grants,
                actor=actor,
                command_ref=command_ref,
            )
        if name in {"github.write", "github_write", "run_github_write"}:
            return run_github_write(
                store=self.store,
                policy=policy,
                grants=grants,
                actor=actor,
                operation=str(arguments.get("operation") or "write"),
                target=str(arguments.get("target") or ""),
            )
        return None


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


def _intent_stop_reason(intent_lock: IntentLock | None, step: LoopStep) -> str | None:
    if intent_lock is None:
        return None
    trigger = step.context.get("trigger_stop_condition")
    if trigger is None:
        return None
    if str(trigger) in intent_lock.stop_conditions:
        return f"intent stop condition triggered: {trigger}"
    return None


def _request_id(run_id: str, index: int, phase: TaskRunPhase, tool_round: int) -> str:
    base = f"runner_step_request_{run_id}_{index}_{phase}"
    if tool_round == 0:
        return base
    return f"{base}_tool_round_{tool_round}"


def _message_history_from_context(context: dict[str, object]) -> list[dict[str, str]]:
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


def _context_with_message_history(
    context: dict[str, object],
    message_history: list[dict[str, str]],
) -> dict[str, object]:
    if not message_history:
        return dict(context)
    return {**context, "message_history": list(message_history)}


def _dispatchable_tool_calls(result: RunnerStepResult) -> list[dict[str, Any]]:
    raw_tool_calls = result.observed_output.get("tool_calls", [])
    if not isinstance(raw_tool_calls, list):
        return []
    tool_calls: list[dict[str, Any]] = []
    for raw_tool_call in raw_tool_calls:
        if not isinstance(raw_tool_call, dict):
            continue
        if _tool_name(raw_tool_call) in {
            "shell.execute",
            "shell_execute",
            "run_shell_command_ref",
            "github.write",
            "github_write",
            "run_github_write",
        }:
            tool_calls.append(raw_tool_call)
    return tool_calls


def _result_with_stream_chunks(
    result: RunnerStepResult,
    stream_chunks: list[str],
) -> RunnerStepResult:
    observed_output = {
        **result.observed_output,
        "stream_chunks": list(stream_chunks),
        "stream_text": "".join(stream_chunks),
    }
    return result.model_copy(update={"observed_output": observed_output})


def _tool_name(tool_call: dict[str, Any]) -> str:
    name = tool_call.get("name")
    if name is not None:
        return str(name)
    function = tool_call.get("function")
    if isinstance(function, dict) and function.get("name") is not None:
        return str(function["name"])
    return ""


def _tool_arguments(tool_call: dict[str, Any]) -> dict[str, Any]:
    raw_arguments: Any = tool_call.get("arguments")
    function = tool_call.get("function")
    if raw_arguments is None and isinstance(function, dict):
        raw_arguments = function.get("arguments")
    if raw_arguments is None:
        raw_arguments = tool_call.get("input", {})
    if isinstance(raw_arguments, dict):
        return raw_arguments
    if isinstance(raw_arguments, str) and raw_arguments:
        try:
            parsed = json.loads(raw_arguments)
        except json.JSONDecodeError:
            return {"raw": raw_arguments}
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    return {}


def _tool_message(tool_call: dict[str, Any], side_effect: SideEffectResult) -> dict[str, str]:
    content = {
        "allowed": side_effect.allowed,
        "receipt_id": side_effect.receipt.id,
        "summary": side_effect.receipt.result.summary,
        "output": side_effect.output or {},
    }
    tool_call_id = tool_call.get("id") or tool_call.get("call_id") or _tool_name(tool_call)
    return {
        "role": "tool",
        "tool_call_id": str(tool_call_id),
        "content": json.dumps(content, sort_keys=True),
    }


def _receipt_slug(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")
