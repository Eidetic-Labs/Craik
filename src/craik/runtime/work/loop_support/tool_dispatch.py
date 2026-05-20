"""Tool-call dispatch helpers for the governed execution loop."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from craik.contracts.models import (
    CapabilityGrant,
    PolicyEnvelope,
    RunnerStepResult,
    SandboxBackend,
    ToolAttestationStatus,
    ToolResultAttestation,
)
from craik.runtime.policy.redaction import redact
from craik.runtime.sandbox.local_process_backend import (
    LocalProcessCommandRegistry,
    LocalProcessRequest,
    execute_local_process_command,
)
from craik.runtime.side_effects import (
    SideEffectResult,
    planned_capability_receipt_id,
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
    sandbox_config: object | None = None,
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
            executor=_local_process_executor(
                policy=policy,
                grants=grants,
                command_ref=command_ref,
                sandbox_config=sandbox_config,
            ),
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


def _local_process_executor(
    *,
    policy: PolicyEnvelope,
    grants: list[CapabilityGrant],
    command_ref: str,
    sandbox_config: object | None,
) -> Any | None:
    if not isinstance(sandbox_config, dict):
        return None
    raw_backend = sandbox_config.get("backend")
    raw_commands = sandbox_config.get("commands")
    if not isinstance(raw_backend, dict) or not isinstance(raw_commands, dict):
        return None
    backend = SandboxBackend.model_validate(raw_backend)
    registry = LocalProcessCommandRegistry.from_mapping(raw_commands)
    grant_id = _grant_id_for_shell_execute(grants)
    receipt_id = planned_capability_receipt_id(policy, "shell.execute", command_ref)

    def execute(command: str) -> dict[str, Any]:
        request = LocalProcessRequest(
            id=f"local_process_request_{policy.task_id}_{_slug(command)}",
            backend_id=backend.id,
            command_ref=command,
            policy_envelope_id=policy.id,
            capability_grant_id=grant_id,
            receipt_id=receipt_id,
        )
        result = execute_local_process_command(
            backend=backend,
            request=request,
            registry=registry,
        )
        return result.model_dump(mode="json")

    return execute


def _grant_id_for_shell_execute(grants: list[CapabilityGrant]) -> str | None:
    for grant in grants:
        if grant.capability == "shell.execute":
            return grant.id
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


def tool_message(
    tool_call: dict[str, Any],
    side_effect: SideEffectResult,
    *,
    attestation_id: str | None = None,
) -> dict[str, str]:
    """Build the provider-facing tool response message for a side effect."""
    content = {
        "allowed": side_effect.allowed,
        "receipt_id": side_effect.receipt.id,
        "attestation_id": attestation_id,
        "summary": side_effect.receipt.result.summary,
        "output": side_effect.output or {},
    }
    tool_call_id = tool_call.get("id") or tool_call.get("call_id") or tool_name(tool_call)
    return {
        "role": "tool",
        "tool_call_id": str(tool_call_id),
        "content": json.dumps(content, sort_keys=True),
    }


def tool_result_attestation(
    *,
    task_id: str,
    case_file_id: str,
    tool_call: dict[str, Any],
    side_effect: SideEffectResult,
) -> ToolResultAttestation:
    """Build a durable attestation for the exact tool payload replayed to the model."""
    name = tool_name(tool_call)
    tool_call_id = str(tool_call.get("id") or tool_call.get("call_id") or name)
    output = redact(side_effect.output or {}).value
    output_hash = _hash_payload(
        {
            "allowed": side_effect.allowed,
            "receipt_id": side_effect.receipt.id,
            "summary": side_effect.receipt.result.summary,
            "output": output,
        }
    )
    status: ToolAttestationStatus = "attested" if side_effect.allowed else "blocked"
    return ToolResultAttestation(
        id=f"attestation_{task_id}_{_slug(tool_call_id)}",
        task_id=task_id,
        case_file_id=case_file_id,
        tool_name=name,
        tool_identity=tool_call_id,
        command=_command_summary(name, tool_arguments(tool_call)),
        observed_output_summary=(
            f"Tool {name} {'returned' if side_effect.allowed else 'was blocked with'} "
            f"receipt {side_effect.receipt.id}."
        ),
        output_hash=output_hash,
        trust_class="observed" if side_effect.allowed else "policy",
        status=status,
        receipt_id=side_effect.receipt.id,
        captured_at=datetime.now(UTC),
    )


def attested_tool_message(
    *,
    store: LocalStore,
    task_id: str,
    case_file_id: str,
    tool_call: dict[str, Any],
    side_effect: SideEffectResult,
) -> dict[str, str]:
    """Persist a tool-result attestation and return the replay message."""
    attestation = tool_result_attestation(
        task_id=task_id,
        case_file_id=case_file_id,
        tool_call=tool_call,
        side_effect=side_effect,
    )
    store.put_tool_result_attestation(attestation)
    return tool_message(tool_call, side_effect, attestation_id=attestation.id)


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


def _hash_payload(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _command_summary(name: str, arguments: dict[str, Any]) -> str | None:
    if name in {"shell.execute", "shell_execute", "run_shell_command_ref"}:
        return str(
            arguments.get("command_ref")
            or arguments.get("command")
            or arguments.get("target")
            or ""
        )
    if name in {"github.write", "github_write", "run_github_write"}:
        return str(arguments.get("operation") or "write")
    return None


def _slug(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")
