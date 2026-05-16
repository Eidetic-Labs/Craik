"""Codex-compatible runner adapter preview."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, cast

from craik.contracts.models import (
    CompiledPrompt,
    RunnerAdapterRequest,
    RunnerAdapterResult,
    RunnerMetadata,
    RunnerResultStatus,
)
from craik.runtime.runners import get_runner_capability_matrix

CODEX_RUNNER_ID = "codex"
CODEX_ADAPTER_VERSION = "0.2.0-preview"


class CodexRunnerAdapterError(RuntimeError):
    """Base error for Codex adapter failures."""


class CodexRunnerRequestError(CodexRunnerAdapterError):
    """Raised when a request cannot be handled by the Codex adapter."""


@dataclass(frozen=True)
class CodexRunnerAdapter:
    """Preview adapter for Codex-compatible prompt handoff and fixture runs."""

    adapter_version: str = CODEX_ADAPTER_VERSION
    fixture_status: RunnerResultStatus = "completed"
    live_available: bool = False
    executable: str | None = None
    metadata_extra: dict[str, Any] = field(default_factory=dict)

    @property
    def metadata(self) -> RunnerMetadata:
        """Return Codex runner metadata with preview adapter details."""
        base = get_runner_capability_matrix(CODEX_RUNNER_ID).runner
        mode = "live" if self.live_available else "fixture"
        metadata = {
            "adapter_mode": mode,
            "live_available": self.live_available,
            "fixture_status": self.fixture_status,
        }
        if self.executable:
            metadata["executable"] = self.executable
        metadata.update(self.metadata_extra)
        return base.model_copy(
            update={
                "adapter_version": self.adapter_version,
                "mode": mode,
                "metadata": metadata,
            }
        )

    def run(self, request: RunnerAdapterRequest) -> RunnerAdapterResult:
        """Return a normalized Codex runner result for a compiled prompt request."""
        if request.runner.id != CODEX_RUNNER_ID:
            raise CodexRunnerRequestError(
                f"Codex adapter cannot run request for runner {request.runner.id!r}"
            )

        status = _status_from_context(request.context, self.fixture_status)
        summary = _summary_from_context(request.context, status)
        diagnostics = _diagnostics(request.context, self.live_available)
        receipt_inputs = _receipt_inputs(request, status, summary)
        handoff_input = _handoff_input(request, status, summary)
        metadata = self.metadata

        return RunnerAdapterResult(
            id=f"runner_result_{request.id}",
            request_id=request.id,
            task_id=request.task_id,
            runner=metadata,
            status=status,
            summary=summary,
            outputs={
                "prompt_handoff": {
                    "runner_id": CODEX_RUNNER_ID,
                    "prompt": _prompt_from_context(request.context),
                },
                "handoff_input": handoff_input,
                "receipt_inputs": receipt_inputs,
                "runner_metadata": metadata.model_dump(mode="json", by_alias=True),
            },
            receipt_ids=_string_list(request.context.get("receipt_ids")),
            handoff_id=_optional_string(request.context.get("handoff_id")),
            memory_proposal_ids=_string_list(request.context.get("memory_proposal_ids")),
            artifacts=[request.case_file_id, request.policy_envelope_id],
            diagnostics=diagnostics,
            created_at=request.created_at,
        )


def request_from_compiled_prompt(
    compiled: CompiledPrompt,
    *,
    created_at: datetime | None = None,
    adapter: CodexRunnerAdapter | None = None,
    context: dict[str, Any] | None = None,
) -> RunnerAdapterRequest:
    """Build a Codex runner request from a compiled prompt."""
    codex = adapter or CodexRunnerAdapter()
    if compiled.runner_id != CODEX_RUNNER_ID:
        raise CodexRunnerRequestError(
            f"compiled prompt runner {compiled.runner_id!r} is not {CODEX_RUNNER_ID!r}"
        )
    extra_context = context or {}
    return RunnerAdapterRequest(
        id=f"runner_request_{compiled.id}",
        task_id=compiled.task_id,
        runner=codex.metadata,
        task_request_id=compiled.task_id,
        case_file_id=compiled.case_file_id,
        policy_envelope_id=compiled.policy_envelope_id,
        capability_grant_ids=compiled.capability_grant_ids,
        expected_output_schemas=compiled.expected_output_schemas,
        context={
            "compiled_prompt_id": compiled.id,
            "prompt": compiled.prompt,
            "context_omissions": compiled.context_omissions,
            "stop_conditions": compiled.stop_conditions,
            **extra_context,
        },
        created_at=created_at or datetime.now(UTC),
    )


def _status_from_context(
    context: dict[str, Any],
    default: RunnerResultStatus,
) -> RunnerResultStatus:
    value = context.get("fixture_status", default)
    if value not in {"completed", "blocked", "failed", "partial"}:
        raise CodexRunnerRequestError(f"unsupported Codex fixture status: {value!r}")
    return cast(RunnerResultStatus, value)


def _summary_from_context(context: dict[str, Any], status: RunnerResultStatus) -> str:
    if isinstance(context.get("fixture_summary"), str):
        return cast(str, context["fixture_summary"])
    if status == "completed":
        return "Codex fixture completed the compiled prompt handoff."
    if status == "blocked":
        reason = _optional_string(context.get("blocked_reason")) or "policy or approval boundary"
        return f"Codex fixture blocked before execution: {reason}."
    if status == "failed":
        reason = _optional_string(context.get("failure_reason")) or "fixture failure requested"
        return f"Codex fixture failed before completing execution: {reason}."
    return "Codex fixture returned a partial result."


def _diagnostics(context: dict[str, Any], live_available: bool) -> list[str]:
    diagnostics = _string_list(context.get("diagnostics"))
    if not live_available:
        diagnostics.append("Codex live execution unavailable; fixture/prompt-handoff mode used.")
    return diagnostics


def _receipt_inputs(
    request: RunnerAdapterRequest,
    status: RunnerResultStatus,
    summary: str,
) -> list[dict[str, Any]]:
    return [
        {
            "id": f"receipt_input_{request.id}_{index}",
            "task_id": request.task_id,
            "actor": "runner:codex",
            "capability_grant_id": grant_id,
            "capability": "runner.codex",
            "target": request.case_file_id,
            "result": {"status": _receipt_status(status), "summary": summary},
        }
        for index, grant_id in enumerate(request.capability_grant_ids, start=1)
    ]


def _handoff_input(
    request: RunnerAdapterRequest,
    status: RunnerResultStatus,
    summary: str,
) -> dict[str, Any]:
    return {
        "task_id": request.task_id,
        "agent": "runner:codex",
        "status": _handoff_status(status),
        "summary": summary,
        "artifacts": [request.case_file_id, request.policy_envelope_id],
        "tests_run": _string_list(request.context.get("tests_run")),
        "risks": _string_list(request.context.get("risks")),
        "next_steps": _string_list(request.context.get("next_steps")),
    }


def _receipt_status(status: RunnerResultStatus) -> str:
    if status == "completed":
        return "passed"
    if status == "blocked":
        return "blocked"
    if status == "failed":
        return "failed"
    return "skipped"


def _handoff_status(status: RunnerResultStatus) -> str:
    if status == "completed":
        return "completed"
    if status == "blocked":
        return "blocked"
    if status == "failed":
        return "failed"
    return "incomplete"


def _prompt_from_context(context: dict[str, Any]) -> str:
    value = context.get("prompt")
    return value if isinstance(value, str) else ""


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    return []
