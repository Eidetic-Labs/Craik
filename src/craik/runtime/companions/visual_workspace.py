"""Live visual workspace and canvas posture decisions."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from craik.contracts.models import CraikModel

VisualWorkspaceSupportLevel = Literal["supported", "experimental", "deferred"]
VisualWorkspaceStatus = Literal["allowed", "review_required", "deferred", "blocked"]


class VisualWorkspaceSurface(CraikModel):
    """Candidate visual workspace or canvas surface."""

    id: str
    support_level: VisualWorkspaceSupportLevel
    read_only: bool = True
    preserves_work_graph_links: bool = True
    preserves_evidence_links: bool = True
    requires_receipts: bool = True
    visual_state_redacted: bool = True
    accessibility_controls: bool = True
    stores_raw_canvas_payloads: bool = False
    docs_ref: str | None = None


class VisualWorkspaceDecision(CraikModel):
    """Decision describing whether a visual workspace surface can be used."""

    status: VisualWorkspaceStatus
    allowed: bool
    reason: str
    surface_id: str
    required_controls: list[str] = Field(default_factory=list)


def visual_workspace_decision(surface: VisualWorkspaceSurface) -> VisualWorkspaceDecision:
    """Evaluate live visual workspace and canvas posture."""
    if surface.stores_raw_canvas_payloads:
        return _blocked(surface, "visual workspace surfaces must not persist raw canvas payloads")
    if not surface.read_only:
        return _blocked(surface, "visual workspace mutation requires a later explicit bridge")
    if not surface.visual_state_redacted:
        return _blocked(surface, "visual workspace state requires redaction")
    if not surface.accessibility_controls:
        return _blocked(surface, "visual workspace surfaces require accessibility controls")
    if not surface.preserves_work_graph_links:
        return _blocked(surface, "visual workspace surfaces must preserve work graph links")
    if not surface.preserves_evidence_links:
        return _blocked(surface, "visual workspace surfaces must preserve evidence links")
    if not surface.requires_receipts:
        return _blocked(surface, "visual workspace surfaces require receipts")
    if surface.support_level == "deferred":
        return VisualWorkspaceDecision(
            status="deferred",
            allowed=False,
            reason="visual workspace surface is deferred by product posture",
            surface_id=surface.id,
            required_controls=_controls(surface),
        )
    if surface.support_level == "experimental":
        return VisualWorkspaceDecision(
            status="review_required",
            allowed=False,
            reason="experimental visual workspace surfaces require explicit review",
            surface_id=surface.id,
            required_controls=_controls(surface),
        )
    return VisualWorkspaceDecision(
        status="allowed",
        allowed=True,
        reason=(
            "visual workspace surface preserves read-only graph, evidence, receipt, redaction, "
            "and accessibility controls"
        ),
        surface_id=surface.id,
        required_controls=_controls(surface),
    )


def _blocked(surface: VisualWorkspaceSurface, reason: str) -> VisualWorkspaceDecision:
    return VisualWorkspaceDecision(
        status="blocked",
        allowed=False,
        reason=reason,
        surface_id=surface.id,
        required_controls=_controls(surface),
    )


def _controls(surface: VisualWorkspaceSurface) -> list[str]:
    controls = ["read_only", "visual_state_redaction", "accessibility_controls"]
    if surface.preserves_work_graph_links:
        controls.append("work_graph_links")
    if surface.preserves_evidence_links:
        controls.append("evidence_links")
    if surface.requires_receipts:
        controls.append("receipts")
    if surface.docs_ref:
        controls.append("documented_decision")
    return controls
