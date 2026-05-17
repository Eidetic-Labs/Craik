"""Browser and tool execution boundary decisions."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from craik.contracts.models import CraikModel, SandboxBackend

BrowserToolDecisionStatus = Literal["allowed", "denied"]


class BrowserToolRequest(CraikModel):
    """Policy-bound browser or tool execution request."""

    id: str
    backend_id: str
    tool_name: str
    capability: str
    action_ref: str
    policy_envelope_id: str | None = None
    capability_grant_id: str | None = None
    receipt_id: str | None = None
    result_metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserToolDecision(CraikModel):
    """Decision for a browser/tool execution request."""

    status: BrowserToolDecisionStatus
    allowed: bool
    reason: str
    backend_id: str
    tool_name: str
    action_ref: str
    redacted_result_metadata: dict[str, Any] = Field(default_factory=dict)
    required_controls: list[str] = Field(default_factory=list)


def browser_tool_decision(
    *,
    backend: SandboxBackend,
    request: BrowserToolRequest,
) -> BrowserToolDecision:
    """Evaluate whether a browser/tool request preserves execution boundaries."""
    controls = ["policy_envelope", "capability_grant", "receipt", "redaction"]
    redacted_metadata = _redacted_result_metadata(request.result_metadata)
    if backend.kind != "browser_tool" or backend.isolation_mode != "browser":
        return _denied(
            request,
            "browser/tool requests require a browser_tool backend with browser isolation",
            controls,
            redacted_metadata,
        )
    if request.backend_id != backend.id:
        return _denied(
            request,
            f"request targets {request.backend_id}, not {backend.id}",
            controls,
            redacted_metadata,
        )
    if not _supports_capability(backend, request.capability):
        return _denied(
            request,
            f"backend does not declare {request.capability} support",
            controls,
            redacted_metadata,
        )
    if not request.policy_envelope_id:
        return _denied(
            request,
            "browser/tool execution requires a policy envelope",
            controls,
            redacted_metadata,
        )
    if not request.capability_grant_id:
        return _denied(
            request,
            "browser/tool execution requires a capability grant",
            controls,
            redacted_metadata,
        )
    if not request.receipt_id:
        return _denied(
            request,
            "browser/tool execution requires a receipt",
            controls,
            redacted_metadata,
        )
    return BrowserToolDecision(
        status="allowed",
        allowed=True,
        reason="browser/tool request is policy-, grant-, receipt-, and redaction-bound",
        backend_id=backend.id,
        tool_name=request.tool_name,
        action_ref=request.action_ref,
        redacted_result_metadata=redacted_metadata,
        required_controls=controls,
    )


def _supports_capability(backend: SandboxBackend, capability_name: str) -> bool:
    return any(capability.name == capability_name for capability in backend.capabilities)


def _redacted_result_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in metadata.items():
        normalized = key.lower().replace("-", "_")
        if normalized in _REDACTED_RESULT_KEYS:
            continue
        if any(token in normalized for token in _SECRET_KEY_TOKENS):
            continue
        redacted[key] = value
    return redacted


def _denied(
    request: BrowserToolRequest,
    reason: str,
    controls: list[str],
    redacted_metadata: dict[str, Any],
) -> BrowserToolDecision:
    return BrowserToolDecision(
        status="denied",
        allowed=False,
        reason=reason,
        backend_id=request.backend_id,
        tool_name=request.tool_name,
        action_ref=request.action_ref,
        redacted_result_metadata=redacted_metadata,
        required_controls=controls,
    )


_REDACTED_RESULT_KEYS = {
    "body",
    "cookies",
    "dom",
    "headers",
    "html",
    "payload",
    "screenshot",
    "storage_state",
    "text",
}
_SECRET_KEY_TOKENS = ("secret", "token", "api_key", "apikey", "password", "credential")
