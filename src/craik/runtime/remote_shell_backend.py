"""SSH and remote shell backend boundaries."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel, SandboxBackend

RemoteShellDecisionStatus = Literal["allowed", "denied"]


class RemoteShellTarget(CraikModel):
    """Non-secret remote shell target metadata."""

    id: str
    host_ref: str
    user_ref: str | None = None
    port_ref: str | None = None
    auth_ref_name: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_remote_shell_target(self) -> RemoteShellTarget:
        """Reject inline credentials and secret-like metadata."""
        for value, field_name in (
            (self.host_ref, "host_ref"),
            (self.user_ref, "user_ref"),
            (self.port_ref, "port_ref"),
        ):
            if value is not None:
                _reject_inline_secret(value, field_name)
        for key in self.metadata:
            normalized = key.lower().replace("-", "_")
            if any(token in normalized for token in _SECRET_KEY_TOKENS):
                raise ValueError("remote shell target metadata must not contain secret-like keys")
        return self


class RemoteShellRequest(CraikModel):
    """Policy-bound request for remote shell command execution."""

    id: str
    backend_id: str
    target_id: str
    command_ref: str
    operation: Literal["run"] = "run"
    capability: Literal["shell.remote.execute"] = "shell.remote.execute"
    policy_envelope_id: str | None = None
    capability_grant_id: str | None = None
    receipt_id: str | None = None


class RemoteShellDecision(CraikModel):
    """Decision for a remote shell backend request."""

    status: RemoteShellDecisionStatus
    allowed: bool
    reason: str
    backend_id: str
    target_id: str
    command_ref: str
    receipt_id: str | None = None
    required_controls: list[str] = Field(default_factory=list)


def remote_shell_decision(
    *,
    backend: SandboxBackend,
    target: RemoteShellTarget,
    request: RemoteShellRequest,
) -> RemoteShellDecision:
    """Evaluate whether a remote shell request preserves security boundaries."""
    controls = ["policy_envelope", "capability_grant", "receipt", "redaction", "external_auth_ref"]
    if backend.kind != "remote_shell" or backend.isolation_mode != "remote":
        return _denied(
            target,
            request,
            "remote shell requests require a remote_shell backend with remote isolation",
            controls,
        )
    if request.backend_id != backend.id:
        return _denied(
            target,
            request,
            f"request targets {request.backend_id}, not {backend.id}",
            controls,
        )
    if request.target_id != target.id:
        return _denied(
            target,
            request,
            f"request targets {request.target_id}, not {target.id}",
            controls,
        )
    if not _supports_remote_shell_execute(backend):
        return _denied(
            request.target_id,
            request,
            "backend does not declare shell.remote.execute run support",
            controls,
        )
    if not target.auth_ref_name:
        return _denied(
            target,
            request,
            "remote shell execution requires an external auth reference",
            controls,
        )
    if not request.policy_envelope_id:
        return _denied(
            target,
            request,
            "remote shell execution requires a policy envelope",
            controls,
        )
    if not request.capability_grant_id:
        return _denied(
            target,
            request,
            "remote shell execution requires a capability grant",
            controls,
        )
    if not request.receipt_id:
        return _denied(target, request, "remote shell execution requires a receipt", controls)
    if _looks_like_inline_shell(request.command_ref):
        return _denied(
            target,
            request,
            "remote shell requests require command references, not inline shell",
            controls,
        )
    return RemoteShellDecision(
        status="allowed",
        allowed=True,
        reason="remote shell request is target-, policy-, grant-, and receipt-bound",
        backend_id=backend.id,
        target_id=target.id,
        command_ref=request.command_ref,
        receipt_id=request.receipt_id,
        required_controls=controls,
    )


def _supports_remote_shell_execute(backend: SandboxBackend) -> bool:
    return any(
        capability.name == "shell.remote.execute" and "run" in capability.operations
        for capability in backend.capabilities
    )


def _looks_like_inline_shell(command_ref: str) -> bool:
    shell_tokens = (" ", "&&", "||", ";", "|", "$(", "`")
    return any(token in command_ref for token in shell_tokens)


def _denied(
    target: RemoteShellTarget | str,
    request: RemoteShellRequest,
    reason: str,
    controls: list[str],
) -> RemoteShellDecision:
    target_id = target if isinstance(target, str) else target.id
    return RemoteShellDecision(
        status="denied",
        allowed=False,
        reason=reason,
        backend_id=request.backend_id,
        target_id=target_id,
        command_ref=request.command_ref,
        receipt_id=request.receipt_id,
        required_controls=controls,
    )


def _reject_inline_secret(value: str, field_name: str) -> None:
    normalized = value.lower()
    if "@" in value or any(token in normalized for token in _SECRET_VALUE_TOKENS):
        raise ValueError(f"{field_name} must not contain inline credentials")


_SECRET_KEY_TOKENS = ("secret", "token", "api_key", "apikey", "password", "credential")
_SECRET_VALUE_TOKENS = ("token=", "api_key=", "apikey=", "password=", "secret=")
