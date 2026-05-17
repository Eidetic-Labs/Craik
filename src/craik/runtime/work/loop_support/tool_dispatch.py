"""Tool-call dispatch helpers for the governed execution loop."""

from __future__ import annotations

import json
from typing import Any

from craik.contracts.models import (
    CapabilityGrant,
    PolicyEnvelope,
    RunnerStepResult,
)
from craik.runtime.side_effects import (
    SideEffectResult,
    run_github_write,
    run_shell_command_ref,
)
from craik.runtime.store import LocalStore

DISPATCHABLE_TOOL_NAMES = {
    "shell.execute",
    "shell_execute",
    "run_shell_command_ref",
    "github.write",
    "github_write",
    "run_github_write",
}


def dispatchable_tool_calls(result: RunnerStepResult) -> list[dict[str, Any]]:
    """Return tool calls that the loop knows how to dispatch."""
    raw_tool_calls = result.observed_output.get("tool_calls", [])
    if not isinstance(raw_tool_calls, list):
        return []
    tool_calls: list[dict[str, Any]] = []
    for raw_tool_call in raw_tool_calls:
        if not isinstance(raw_tool_call, dict):
            continue
        if tool_name(raw_tool_call) in DISPATCHABLE_TOOL_NAMES:
            tool_calls.append(raw_tool_call)
    return tool_calls


def dispatch_tool_call_side_effect(
    *,
    store: LocalStore,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    tool_call: dict[str, Any],
    actor: str,
) -> SideEffectResult | None:
    """Dispatch a policy-gated side effect for a provider tool call."""
    name = tool_name(tool_call)
    arguments = tool_arguments(tool_call)
    if name in {"shell.execute", "shell_execute", "run_shell_command_ref"}:
        command_ref = str(
            arguments.get("command_ref")
            or arguments.get("command")
            or arguments.get("target")
            or ""
        )
        return run_shell_command_ref(
            store=store,
            policy=policy,
            grants=grants,
            actor=actor,
            command_ref=command_ref,
        )
    if name in {"github.write", "github_write", "run_github_write"}:
        return run_github_write(
            store=store,
            policy=policy,
            grants=grants,
            actor=actor,
            operation=str(arguments.get("operation") or "write"),
            target=str(arguments.get("target") or ""),
        )
    return None


def result_with_stream_chunks(
    result: RunnerStepResult,
    stream_chunks: list[str],
) -> RunnerStepResult:
    """Attach replayable streaming chunks to a runner step result."""
    observed_output = {
        **result.observed_output,
        "stream_chunks": list(stream_chunks),
        "stream_text": "".join(stream_chunks),
    }
    return result.model_copy(update={"observed_output": observed_output})


def tool_message(tool_call: dict[str, Any], side_effect: SideEffectResult) -> dict[str, str]:
    """Build the provider-facing tool response message for a side effect."""
    content = {
        "allowed": side_effect.allowed,
        "receipt_id": side_effect.receipt.id,
        "summary": side_effect.receipt.result.summary,
        "output": side_effect.output or {},
    }
    tool_call_id = tool_call.get("id") or tool_call.get("call_id") or tool_name(tool_call)
    return {
        "role": "tool",
        "tool_call_id": str(tool_call_id),
        "content": json.dumps(content, sort_keys=True),
    }


def tool_name(tool_call: dict[str, Any]) -> str:
    """Return a normalized tool name from direct or function-call shapes."""
    name = tool_call.get("name")
    if name is not None:
        return str(name)
    function = tool_call.get("function")
    if isinstance(function, dict) and function.get("name") is not None:
        return str(function["name"])
    return ""


def tool_arguments(tool_call: dict[str, Any]) -> dict[str, Any]:
    """Return decoded tool arguments from direct, function, or input shapes."""
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
