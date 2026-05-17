"""Docker sandbox backend boundaries."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel, SandboxBackend

DockerNetworkMode = Literal["none", "bridge", "restricted"]
DockerMountMode = Literal["read_only", "read_write"]
DockerDecisionStatus = Literal["allowed", "denied"]


class DockerMount(CraikModel):
    """Explicit container mount reference."""

    source_ref: str
    target_path: str
    mode: DockerMountMode = "read_only"


class DockerSandboxRequest(CraikModel):
    """Policy-bound Docker sandbox request."""

    id: str
    backend_id: str
    image_ref: str
    command_ref: str
    network_mode: DockerNetworkMode = "none"
    mounts: list[DockerMount] = Field(default_factory=list)
    env_ref_names: list[str] = Field(default_factory=list)
    privileged: bool = False
    policy_envelope_id: str | None = None
    capability_grant_id: str | None = None
    receipt_id: str | None = None

    @model_validator(mode="after")
    def validate_docker_request(self) -> DockerSandboxRequest:
        """Keep Docker requests explicit and non-secret."""
        _reject_secret_like_ref(self.image_ref, "image_ref")
        _reject_secret_like_ref(self.command_ref, "command_ref")
        for mount in self.mounts:
            _reject_secret_like_ref(mount.source_ref, "mount source_ref")
        return self


class DockerSandboxDecision(CraikModel):
    """Decision for a Docker sandbox request."""

    status: DockerDecisionStatus
    allowed: bool
    reason: str
    backend_id: str
    image_ref: str
    command_ref: str
    network_mode: DockerNetworkMode
    required_controls: list[str] = Field(default_factory=list)


def docker_sandbox_decision(
    *,
    backend: SandboxBackend,
    request: DockerSandboxRequest,
) -> DockerSandboxDecision:
    """Evaluate whether a Docker sandbox request preserves container boundaries."""
    controls = ["policy_envelope", "capability_grant", "receipt", "redaction", "explicit_isolation"]
    if backend.kind != "container" or backend.isolation_mode != "container":
        return _denied(
            request,
            "Docker requests require a container backend with container isolation",
            controls,
        )
    if request.backend_id != backend.id:
        return _denied(request, f"request targets {request.backend_id}, not {backend.id}", controls)
    if not _supports_container_run(backend):
        return _denied(request, "backend does not declare container.run support", controls)
    if request.privileged:
        return _denied(request, "Docker sandbox requests must not be privileged", controls)
    if request.network_mode == "bridge":
        return _denied(request, "Docker sandbox network mode must be none or restricted", controls)
    if any(mount.mode == "read_write" for mount in request.mounts):
        return _denied(request, "Docker sandbox mounts must be read-only by default", controls)
    if not request.policy_envelope_id:
        return _denied(request, "Docker sandbox execution requires a policy envelope", controls)
    if not request.capability_grant_id:
        return _denied(request, "Docker sandbox execution requires a capability grant", controls)
    if not request.receipt_id:
        return _denied(request, "Docker sandbox execution requires a receipt", controls)
    return DockerSandboxDecision(
        status="allowed",
        allowed=True,
        reason="Docker sandbox request is isolated, policy-bound, and receipt-ready",
        backend_id=backend.id,
        image_ref=request.image_ref,
        command_ref=request.command_ref,
        network_mode=request.network_mode,
        required_controls=controls,
    )


def _supports_container_run(backend: SandboxBackend) -> bool:
    return any(
        capability.name == "container.run" and "run" in capability.operations
        for capability in backend.capabilities
    )


def _denied(
    request: DockerSandboxRequest,
    reason: str,
    controls: list[str],
) -> DockerSandboxDecision:
    return DockerSandboxDecision(
        status="denied",
        allowed=False,
        reason=reason,
        backend_id=request.backend_id,
        image_ref=request.image_ref,
        command_ref=request.command_ref,
        network_mode=request.network_mode,
        required_controls=controls,
    )


def _reject_secret_like_ref(value: str, field_name: str) -> None:
    normalized = value.lower()
    secret_tokens = ("token=", "api_key=", "apikey=", "password=", "secret=")
    if any(token in normalized for token in secret_tokens):
        raise ValueError(f"{field_name} must not contain secret-like values")
