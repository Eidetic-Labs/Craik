"""Adjacent runtime bridge posture decisions."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from craik.contracts.models import CraikModel

AdjacentRuntimeBridgeSupportLevel = Literal["supported", "experimental", "deferred"]
AdjacentRuntimeBridgeStatus = Literal["allowed", "review_required", "deferred", "blocked"]


class AdjacentRuntimeBridgeSurface(CraikModel):
    """Candidate bridge to an adjacent runtime."""

    id: str
    runtime_name: str
    support_level: AdjacentRuntimeBridgeSupportLevel
    policy_envelope_id: str
    preserves_policy_context: bool = True
    preserves_evidence_links: bool = True
    requires_capability_grant: bool = True
    requires_receipts: bool = True
    redacts_inputs: bool = True
    redacts_outputs: bool = True
    copies_secret_values: bool = False
    grants_unbounded_tool_access: bool = False
    accepts_runtime_instructions_as_authoritative: bool = False
    mutates_without_operator_approval: bool = False
    docs_ref: str | None = None


class AdjacentRuntimeBridgeDecision(CraikModel):
    """Decision describing whether an adjacent runtime bridge can be used."""

    status: AdjacentRuntimeBridgeStatus
    allowed: bool
    reason: str
    surface_id: str
    required_controls: list[str] = Field(default_factory=list)


def adjacent_runtime_bridge_decision(
    surface: AdjacentRuntimeBridgeSurface,
) -> AdjacentRuntimeBridgeDecision:
    """Evaluate adjacent runtime bridge posture."""
    if surface.copies_secret_values:
        return _blocked(surface, "adjacent runtime bridges must not copy secret values")
    if surface.grants_unbounded_tool_access:
        return _blocked(surface, "adjacent runtime bridges must not grant unbounded tool access")
    if surface.accepts_runtime_instructions_as_authoritative:
        return _blocked(
            surface,
            "adjacent runtime instructions must not override Craik policy",
        )
    if surface.mutates_without_operator_approval:
        return _blocked(surface, "adjacent runtime mutations require operator approval")
    if not surface.policy_envelope_id:
        return _blocked(surface, "adjacent runtime bridges require policy envelope context")
    if not surface.preserves_policy_context:
        return _blocked(surface, "adjacent runtime bridges must preserve policy context")
    if not surface.preserves_evidence_links:
        return _blocked(surface, "adjacent runtime bridges must preserve evidence links")
    if not surface.requires_capability_grant:
        return _blocked(surface, "adjacent runtime bridges require capability grants")
    if not surface.requires_receipts:
        return _blocked(surface, "adjacent runtime bridges require receipts")
    if not surface.redacts_inputs or not surface.redacts_outputs:
        return _blocked(surface, "adjacent runtime bridges require input and output redaction")
    if surface.support_level == "deferred":
        return AdjacentRuntimeBridgeDecision(
            status="deferred",
            allowed=False,
            reason="adjacent runtime bridge is deferred by product posture",
            surface_id=surface.id,
            required_controls=_controls(surface),
        )
    if surface.support_level == "experimental":
        return AdjacentRuntimeBridgeDecision(
            status="review_required",
            allowed=False,
            reason="experimental adjacent runtime bridges require explicit review",
            surface_id=surface.id,
            required_controls=_controls(surface),
        )
    return AdjacentRuntimeBridgeDecision(
        status="allowed",
        allowed=True,
        reason=(
            "adjacent runtime bridge preserves policy, evidence, capability grant, receipt, "
            "and redaction controls"
        ),
        surface_id=surface.id,
        required_controls=_controls(surface),
    )


def _blocked(
    surface: AdjacentRuntimeBridgeSurface,
    reason: str,
) -> AdjacentRuntimeBridgeDecision:
    return AdjacentRuntimeBridgeDecision(
        status="blocked",
        allowed=False,
        reason=reason,
        surface_id=surface.id,
        required_controls=_controls(surface),
    )


def _controls(surface: AdjacentRuntimeBridgeSurface) -> list[str]:
    controls = ["policy_envelope"]
    if surface.preserves_policy_context:
        controls.append("policy_context")
    if surface.preserves_evidence_links:
        controls.append("evidence_links")
    if surface.requires_capability_grant:
        controls.append("capability_grant")
    if surface.requires_receipts:
        controls.append("receipts")
    if surface.redacts_inputs:
        controls.append("input_redaction")
    if surface.redacts_outputs:
        controls.append("output_redaction")
    if surface.docs_ref:
        controls.append("documented_decision")
    return controls
