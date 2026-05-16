"""Governed single-agent execution loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

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
from craik.runtime.store import LocalStore


class LoopExecutionError(RuntimeError):
    """Base error for governed loop execution failures."""


class LoopPolicyBlockedError(LoopExecutionError):
    """Raised when policy blocks a side-effect step."""


class LoopMaxIterationsError(LoopExecutionError):
    """Raised when the loop reaches its iteration bound."""


class RunnerStepHandler(Protocol):
    """Minimal runner boundary for one loop step."""

    def run_step(self, request: RunnerStepRequest) -> RunnerStepResult:
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

    def run_step(self, request: RunnerStepRequest) -> RunnerStepResult:
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

        for index, step in enumerate(active_steps, start=1):
            if index > max_iterations:
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

            request = RunnerStepRequest(
                id=f"runner_step_request_{run.id}_{index}_{step.phase}",
                run_id=run.id,
                task_id=task_id,
                phase=step.phase,
                runner=runner_metadata,
                policy_envelope_id=policy.id,
                intent_lock_id=intent_lock.id if intent_lock else None,
                capability_grant_ids=[grant.id for grant in active_grants],
                expected_output_schemas=["craik.runner_step_result"],
                input_prompt=step.input_prompt,
                context=step.context,
                created_at=datetime.now(UTC),
            )
            result = self.runner.run_step(request)
            if side_effect_receipt is not None and side_effect_receipt.id not in result.receipt_ids:
                result = result.model_copy(
                    update={"receipt_ids": [*result.receipt_ids, side_effect_receipt.id]}
                )
            capture = self.outputs.capture_step_result(
                result,
                proposal_specs=step.proposal_specs,
            )
            step_results.append(result)
            output_captures.append(capture)

            if result.status in {"blocked", "failed"}:
                terminal_status: TaskRunStatus = (
                    "blocked" if result.status == "blocked" else "failed"
                )
                run = self.runs.transition(
                    run.id,
                    RunTransition(
                        status=terminal_status,
                        phase="stop",
                        iteration=index,
                        receipt_id=side_effect_receipt.id if side_effect_receipt else None,
                        stop_reason=result.summary,
                        at=datetime.now(UTC),
                    ),
                )
                return LoopExecutionResult(run, step_results, output_captures, receipts)

            run = self.runs.transition(
                run.id,
                RunTransition(
                    status="running",
                    phase=step.phase,
                    iteration=index,
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


def _receipt_slug(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")
