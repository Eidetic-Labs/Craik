"""Local process sandbox backend boundaries."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from craik.contracts.models import CraikModel, SandboxBackend

LocalProcessDecisionStatus = Literal["allowed", "denied"]


class LocalProcessRequest(CraikModel):
    """Policy-bound request to run a local process command reference."""

    id: str
    backend_id: str
    command_ref: str
    operation: Literal["run"] = "run"
    capability: Literal["shell.execute"] = "shell.execute"
    policy_envelope_id: str | None = None
    capability_grant_id: str | None = None
    receipt_id: str | None = None
    working_directory_ref: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class LocalProcessDecision(CraikModel):
    """Decision for a local process backend request."""

    status: LocalProcessDecisionStatus
    allowed: bool
    reason: str
    backend_id: str
    command_ref: str
    required_controls: list[str] = Field(default_factory=list)


def local_process_decision(
    *,
    backend: SandboxBackend,
    request: LocalProcessRequest,
) -> LocalProcessDecision:
    """Evaluate whether a local process request preserves execution boundaries."""
    controls = ["policy_envelope", "capability_grant", "receipt", "redaction"]
    if backend.kind != "local_process" or backend.isolation_mode != "process":
        return _denied(
            request,
            "local process requests require a local_process backend with process isolation",
            controls,
        )
    if request.backend_id != backend.id:
        return _denied(request, f"request targets {request.backend_id}, not {backend.id}", controls)
    if not _supports_shell_execute(backend):
        return _denied(request, "backend does not declare shell.execute run support", controls)
    if not request.policy_envelope_id:
        return _denied(request, "local process execution requires a policy envelope", controls)
    if not request.capability_grant_id:
        return _denied(request, "local process execution requires a capability grant", controls)
    if not request.receipt_id:
        return _denied(request, "local process execution requires a receipt", controls)
    if _looks_like_inline_shell(request.command_ref):
        return _denied(
            request,
            "local process requests require command references, not inline shell",
            controls,
        )
    return LocalProcessDecision(
        status="allowed",
        allowed=True,
        reason="local process request is policy-, grant-, and receipt-bound",
        backend_id=backend.id,
        command_ref=request.command_ref,
        required_controls=controls,
    )


def _supports_shell_execute(backend: SandboxBackend) -> bool:
    return any(
        capability.name == "shell.execute" and "run" in capability.operations
        for capability in backend.capabilities
    )


def _looks_like_inline_shell(command_ref: str) -> bool:
    shell_tokens = (" ", "&&", "||", ";", "|", "$(", "`")
    return any(token in command_ref for token in shell_tokens)


def _denied(
    request: LocalProcessRequest,
    reason: str,
    controls: list[str],
) -> LocalProcessDecision:
    return LocalProcessDecision(
        status="denied",
        allowed=False,
        reason=reason,
        backend_id=request.backend_id,
        command_ref=request.command_ref,
        required_controls=controls,
    )
