"""Provider-backed MVP runner orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from craik.contracts.models import (
    CapabilityGrant,
    CompiledPrompt,
    Handoff,
    PolicyEnvelope,
    RunnerResultStatus,
    RunnerStepRequest,
    RunnerStepResult,
    TaskRun,
)
from craik.runtime.case_files import CaseFileAssembler
from craik.runtime.handoffs import HandoffWriter
from craik.runtime.loop import (
    LoopExecutionResult,
    LoopMaxIterationsError,
    LoopStep,
    SingleAgentLoopExecutor,
    default_loop_steps,
)
from craik.runtime.memory import LocalMemoryStore, MemoryStore
from craik.runtime.model_providers import default_model_provider_registry
from craik.runtime.prompts import PromptCompiler
from craik.runtime.provider_runtime import (
    ProviderMessage,
    ProviderRuntimeAdapter,
    ProviderRuntimeRequest,
    ProviderRuntimeResult,
    ProviderTool,
    adapter_for_provider,
    provider_runtime_receipt,
)
from craik.runtime.runners import get_runner_capability_matrix
from craik.runtime.store import LocalStore


@dataclass(frozen=True)
class ProviderBackedRunResult:
    """Completed provider-backed runner path output."""

    compiled_prompt: CompiledPrompt
    loop: LoopExecutionResult | None
    run: TaskRun
    handoff: Handoff
    provider_results: list[ProviderRuntimeResult]
    interrupted_error: str | None = None


@dataclass
class ProviderBackedStepRunner:
    """Deterministic provider-backed step runner for MVP certification."""

    store: LocalStore
    adapter: ProviderRuntimeAdapter
    compiled_prompt: CompiledPrompt
    actor: str
    statuses: list[RunnerResultStatus] = field(default_factory=list)
    provider_results: list[ProviderRuntimeResult] = field(default_factory=list)

    def run_step(self, request: RunnerStepRequest) -> RunnerStepResult:
        """Normalize one runner step through the configured provider adapter."""
        status = self.statuses.pop(0) if self.statuses else "completed"
        provider_request = self._provider_request(request, status=status)
        provider_result = self.adapter.execute(provider_request)
        receipt = provider_runtime_receipt(
            adapter=self.adapter,
            request=provider_request,
            result=provider_result,
            task_id=request.task_id,
            policy_envelope_id=request.policy_envelope_id,
            receipt_id=f"receipt_{request.run_id}_{request.phase}_{self.adapter.config.provider_family}",
            actor=self.actor,
        )
        self.store.put_receipt(receipt)
        self.provider_results.append(provider_result)
        return RunnerStepResult(
            id=f"runner_step_result_{request.run_id}_{request.phase}_{self.adapter.config.provider_family}",
            request_id=request.id,
            run_id=request.run_id,
            task_id=request.task_id,
            phase=request.phase,
            runner=request.runner,
            status=status,
            summary=(
                f"{self.adapter.config.provider_family} provider " f"{request.phase} step {status}."
            ),
            observed_output={
                "provider_id": self.adapter.config.provider_id,
                "provider_family": self.adapter.config.provider_family,
                "model": provider_result.model,
                "response_id": provider_result.response_id,
                "text": provider_result.text,
                "tool_calls": provider_result.tool_calls,
                "structured_output": provider_result.structured_output,
                "usage": provider_result.usage,
            },
            diagnostics=[] if status in {"completed", "partial"} else [provider_result.text],
            receipt_ids=[receipt.id],
            artifacts=[self.compiled_prompt.id],
            created_at=datetime.now(UTC),
        )

    def _provider_request(
        self,
        request: RunnerStepRequest,
        *,
        status: RunnerResultStatus,
    ) -> ProviderRuntimeRequest:
        return ProviderRuntimeRequest(
            messages=[
                ProviderMessage(
                    role="system",
                    content="You are executing a governed Craik MVP runner step.",
                ),
                ProviderMessage(
                    role="user",
                    content=(
                        f"{self.compiled_prompt.prompt}\n\n"
                        f"## Current Step\nPhase: {request.phase}\n{request.input_prompt}"
                    ),
                ),
            ],
            tools=[
                ProviderTool(
                    name="record_runner_step",
                    description="Record the normalized provider-backed runner step.",
                    input_schema=_runner_step_schema(),
                )
            ],
            structured_output_schema=_runner_step_schema(),
            stream=False,
            metadata={
                "user_id": request.task_id,
                "run_id": request.run_id,
                "phase": request.phase,
                "status": status,
                "response_id": f"provider_response_{request.run_id}_{request.phase}",
            },
        )


@dataclass(frozen=True)
class ProviderBackedRunExecutor:
    """Run one complete deterministic provider-backed MVP path."""

    store: LocalStore
    memory: MemoryStore | None = None

    def execute(
        self,
        *,
        task_id: str,
        provider_id: str,
        grants: list[CapabilityGrant] | None = None,
        steps: list[LoopStep] | None = None,
        statuses: list[RunnerResultStatus] | None = None,
        max_iterations: int = 5,
        started_at: datetime | None = None,
    ) -> ProviderBackedRunResult:
        """Compile the case-file prompt, run through a provider, and leave a handoff."""
        case_file = CaseFileAssembler(self.store).latest_for_task(task_id)
        if case_file is None:
            case_file = CaseFileAssembler(self.store).build(task_id)
        provider = default_model_provider_registry().require(provider_id)
        adapter = adapter_for_provider(
            provider,
            live_enabled=bool(provider.metadata.get("live_enabled", False)),
        )
        compiled = PromptCompiler(self.store).compile(
            task_id,
            runner_id=provider.id,
            expected_output_schemas=["craik.runner_step_result", "craik.handoff"],
        )
        policy = self._policy(compiled.policy_envelope_id)
        runner = ProviderBackedStepRunner(
            store=self.store,
            adapter=adapter,
            compiled_prompt=compiled,
            actor=f"runner:{provider.id}",
            statuses=list(statuses or []),
        )
        loop_executor = SingleAgentLoopExecutor(
            store=self.store,
            memory=self.memory or LocalMemoryStore(self.store),
            runner=runner,
        )
        try:
            loop = loop_executor.execute(
                task_id=task_id,
                case_file_id=case_file.id,
                policy=policy,
                runner_metadata=get_runner_capability_matrix(provider.id).runner,
                grants=grants or [],
                steps=steps or default_loop_steps(),
                max_iterations=max_iterations,
                started_at=started_at,
            )
            handoff = HandoffWriter(self.store).create_from_run(
                loop.run.id,
                agent=f"runner:{provider.id}",
                tests_run=["provider-backed deterministic MVP path"],
            )
            updated = self.store.get_task_run(loop.run.id) or loop.run
            return ProviderBackedRunResult(
                compiled_prompt=compiled,
                loop=loop,
                run=updated,
                handoff=handoff,
                provider_results=list(runner.provider_results),
            )
        except LoopMaxIterationsError as error:
            run = _latest_run_for_task(self.store, task_id)
            handoff = HandoffWriter(self.store).create_from_run(
                run.id,
                agent=f"runner:{provider.id}",
                tests_run=["provider-backed deterministic MVP path"],
            )
            updated = self.store.get_task_run(run.id) or run
            return ProviderBackedRunResult(
                compiled_prompt=compiled,
                loop=None,
                run=updated,
                handoff=handoff,
                provider_results=list(runner.provider_results),
                interrupted_error=str(error),
            )

    def _policy(self, policy_id: str) -> PolicyEnvelope:
        policy = self.store.get_policy_envelope(policy_id)
        if policy is None:
            raise ValueError(f"compiled prompt references missing policy: {policy_id}")
        return policy


def _latest_run_for_task(store: LocalStore, task_id: str) -> TaskRun:
    matches = [run for run in store.list_task_runs() if run.task_id == task_id]
    if not matches:
        raise ValueError(f"no task run was recorded for task: {task_id}")
    return matches[-1]


def _runner_step_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "phase": {"type": "string"},
            "status": {"type": "string"},
            "summary": {"type": "string"},
        },
        "required": ["phase", "status", "summary"],
        "additionalProperties": False,
    }
