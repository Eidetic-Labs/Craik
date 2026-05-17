"""Multi-agent workflow bridge posture decisions."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from craik.contracts.models import CraikModel

MultiAgentWorkflowBridgeSupportLevel = Literal["supported", "experimental", "deferred"]
MultiAgentWorkflowBridgeStatus = Literal["allowed", "review_required", "deferred", "blocked"]


class MultiAgentWorkflowBridgeSurface(CraikModel):
    """Candidate bridge to an external multi-agent workflow system."""

    id: str
    workflow_name: str
    support_level: MultiAgentWorkflowBridgeSupportLevel
    policy_envelope_id: str
    preserves_role_boundaries: bool = True
    preserves_queue_boundaries: bool = True
    preserves_approval_gates: bool = True
    preserves_policy_context: bool = True
    preserves_evidence_links: bool = True
    requires_receipts: bool = True
    redacts_payloads: bool = True
    allows_unbounded_dispatch: bool = False
    bypasses_human_approval: bool = False
    merges_agent_identities: bool = False
    copies_secret_values: bool = False
    accepts_external_instructions_as_authoritative: bool = False
    docs_ref: str | None = None


class MultiAgentWorkflowBridgeDecision(CraikModel):
    """Decision describing whether a multi-agent workflow bridge can be used."""

    status: MultiAgentWorkflowBridgeStatus
    allowed: bool
    reason: str
    surface_id: str
    required_controls: list[str] = Field(default_factory=list)


def multi_agent_workflow_bridge_decision(
    surface: MultiAgentWorkflowBridgeSurface,
) -> MultiAgentWorkflowBridgeDecision:
    """Evaluate multi-agent workflow bridge posture."""
    if surface.copies_secret_values:
        return _blocked(surface, "multi-agent workflow bridges must not copy secret values")
    if surface.allows_unbounded_dispatch:
        return _blocked(surface, "multi-agent workflow bridges must not allow unbounded dispatch")
    if surface.bypasses_human_approval:
        return _blocked(surface, "multi-agent workflow bridges must preserve approval gates")
    if surface.merges_agent_identities:
        return _blocked(surface, "multi-agent workflow bridges must preserve agent identities")
    if surface.accepts_external_instructions_as_authoritative:
        return _blocked(
            surface,
            "external workflow instructions must not override Craik policy",
        )
    if not surface.policy_envelope_id:
        return _blocked(surface, "multi-agent workflow bridges require policy envelope context")
    if not surface.preserves_role_boundaries:
        return _blocked(surface, "multi-agent workflow bridges must preserve role boundaries")
    if not surface.preserves_queue_boundaries:
        return _blocked(surface, "multi-agent workflow bridges must preserve queue boundaries")
    if not surface.preserves_approval_gates:
        return _blocked(surface, "multi-agent workflow bridges must preserve approval gates")
    if not surface.preserves_policy_context:
        return _blocked(surface, "multi-agent workflow bridges must preserve policy context")
    if not surface.preserves_evidence_links:
        return _blocked(surface, "multi-agent workflow bridges must preserve evidence links")
    if not surface.requires_receipts:
        return _blocked(surface, "multi-agent workflow bridges require receipts")
    if not surface.redacts_payloads:
        return _blocked(surface, "multi-agent workflow bridges require payload redaction")
    if surface.support_level == "deferred":
        return MultiAgentWorkflowBridgeDecision(
            status="deferred",
            allowed=False,
            reason="multi-agent workflow bridge is deferred by product posture",
            surface_id=surface.id,
            required_controls=_controls(surface),
        )
    if surface.support_level == "experimental":
        return MultiAgentWorkflowBridgeDecision(
            status="review_required",
            allowed=False,
            reason="experimental multi-agent workflow bridges require explicit review",
            surface_id=surface.id,
            required_controls=_controls(surface),
        )
    return MultiAgentWorkflowBridgeDecision(
        status="allowed",
        allowed=True,
        reason=(
            "multi-agent workflow bridge preserves role, queue, approval, policy, evidence, "
            "receipt, and redaction controls"
        ),
        surface_id=surface.id,
        required_controls=_controls(surface),
    )


def _blocked(
    surface: MultiAgentWorkflowBridgeSurface,
    reason: str,
) -> MultiAgentWorkflowBridgeDecision:
    return MultiAgentWorkflowBridgeDecision(
        status="blocked",
        allowed=False,
        reason=reason,
        surface_id=surface.id,
        required_controls=_controls(surface),
    )


def _controls(surface: MultiAgentWorkflowBridgeSurface) -> list[str]:
    controls = ["policy_envelope"]
    if surface.preserves_role_boundaries:
        controls.append("role_boundaries")
    if surface.preserves_queue_boundaries:
        controls.append("queue_boundaries")
    if surface.preserves_approval_gates:
        controls.append("approval_gates")
    if surface.preserves_policy_context:
        controls.append("policy_context")
    if surface.preserves_evidence_links:
        controls.append("evidence_links")
    if surface.requires_receipts:
        controls.append("receipts")
    if surface.redacts_payloads:
        controls.append("payload_redaction")
    if surface.docs_ref:
        controls.append("documented_decision")
    return controls
