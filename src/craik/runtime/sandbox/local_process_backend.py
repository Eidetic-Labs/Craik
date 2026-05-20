"""Local process sandbox backend boundaries."""

from __future__ import annotations

# Local-process execution is restricted to registered argv lists and never uses shell=True.
import subprocess  # nosec B404
import time
from pathlib import Path
from threading import Event
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


class LocalProcessCommand(CraikModel):
    """Registered command reference that can execute without shell expansion."""

    ref: str
    argv: list[str] = Field(min_length=1)
    cwd: Path | None = None
    timeout_seconds: float = 30.0
    metadata: dict[str, str] = Field(default_factory=dict)


class LocalProcessExecution(CraikModel):
    """Observed local process execution result."""

    allowed: bool
    executed: bool
    reason: str
    backend_id: str
    command_ref: str
    argv: list[str] = Field(default_factory=list)
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    timeout_seconds: float | None = None
    cancelled: bool = False


class LocalProcessCommandRegistry:
    """In-memory registry of command references allowed for local execution."""

    def __init__(self, commands: list[LocalProcessCommand] | None = None) -> None:
        self._commands = {command.ref: command for command in commands or []}

    @classmethod
    def from_mapping(cls, mapping: dict[str, object]) -> LocalProcessCommandRegistry:
        commands: list[LocalProcessCommand] = []
        for ref, raw in mapping.items():
            if isinstance(raw, dict):
                commands.append(LocalProcessCommand.model_validate({"ref": ref, **raw}))
            elif isinstance(raw, list):
                commands.append(LocalProcessCommand(ref=ref, argv=[str(item) for item in raw]))
        return cls(commands)

    def get(self, ref: str) -> LocalProcessCommand | None:
        return self._commands.get(ref)


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


def execute_local_process_command(
    *,
    backend: SandboxBackend,
    request: LocalProcessRequest,
    registry: LocalProcessCommandRegistry,
    cancel_event: Event | None = None,
    poll_interval_seconds: float = 0.05,
) -> LocalProcessExecution:
    """Execute a registered command reference after local-process sandbox checks."""
    decision = local_process_decision(backend=backend, request=request)
    if not decision.allowed:
        return _execution_denied(request, decision.reason)
    command = registry.get(request.command_ref)
    if command is None:
        return _execution_denied(request, "command reference is not registered")
    deadline = time.monotonic() + command.timeout_seconds
    # command.argv comes from the command registry, not provider text.
    process = subprocess.Popen(  # nosec B603
        command.argv,
        cwd=command.cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    while True:
        if cancel_event is not None and cancel_event.is_set():
            stdout, stderr = _terminate(process)
            return LocalProcessExecution(
                allowed=True,
                executed=True,
                reason="local process command cancelled",
                backend_id=request.backend_id,
                command_ref=request.command_ref,
                argv=command.argv,
                returncode=process.returncode,
                stdout=stdout,
                stderr=stderr,
                timeout_seconds=command.timeout_seconds,
                cancelled=True,
            )
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            stdout, stderr = _terminate(process)
            return LocalProcessExecution(
                allowed=True,
                executed=True,
                reason="local process command timed out",
                backend_id=request.backend_id,
                command_ref=request.command_ref,
                argv=command.argv,
                returncode=process.returncode,
                stdout=stdout,
                stderr=stderr,
                timeout_seconds=command.timeout_seconds,
            )
        try:
            stdout, stderr = process.communicate(timeout=min(poll_interval_seconds, remaining))
            break
        except subprocess.TimeoutExpired:
            continue
    return LocalProcessExecution(
        allowed=True,
        executed=True,
        reason="local process command completed",
        backend_id=request.backend_id,
        command_ref=request.command_ref,
        argv=command.argv,
        returncode=process.returncode,
        stdout=stdout,
        stderr=stderr,
        timeout_seconds=command.timeout_seconds,
    )


def _supports_shell_execute(backend: SandboxBackend) -> bool:
    return any(
        capability.name == "shell.execute" and "run" in capability.operations
        for capability in backend.capabilities
    )


def _execution_denied(request: LocalProcessRequest, reason: str) -> LocalProcessExecution:
    return LocalProcessExecution(
        allowed=False,
        executed=False,
        reason=reason,
        backend_id=request.backend_id,
        command_ref=request.command_ref,
    )


def _text(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _terminate(process: subprocess.Popen[str]) -> tuple[str, str]:
    process.terminate()
    try:
        stdout, stderr = process.communicate(timeout=1)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
    return stdout, stderr


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
