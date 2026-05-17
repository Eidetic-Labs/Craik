"""MCP server export boundary decisions."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from craik.contracts.models import CraikModel

MCPSurfaceStability = Literal["stable", "experimental", "internal"]
MCPExportStatus = Literal["exportable", "blocked", "review_required"]


class MCPExportSurface(CraikModel):
    """Candidate surface for an MCP server export."""

    id: str
    name: str
    stability: MCPSurfaceStability
    capabilities: list[str] = Field(default_factory=list)
    requires_capability_grant: bool = True
    requires_receipts: bool = True
    exposes_secret_values: bool = False
    exposes_internal_state: bool = False
    docs_ref: str | None = None


class MCPExportDecision(CraikModel):
    """Decision describing whether a surface can be exported over MCP."""

    status: MCPExportStatus
    allowed: bool
    reason: str
    surface_id: str
    required_controls: list[str] = Field(default_factory=list)


def mcp_export_decision(surface: MCPExportSurface) -> MCPExportDecision:
    """Evaluate MCP export eligibility for a candidate surface."""
    if surface.exposes_secret_values:
        return _blocked(surface, "MCP exports must not expose secret values")
    if surface.exposes_internal_state or surface.stability == "internal":
        return _blocked(surface, "MCP exports must not expose unstable internal surfaces")
    if surface.capabilities and not surface.requires_capability_grant:
        return _blocked(surface, "MCP capability surfaces require explicit grants")
    if _needs_receipts(surface.capabilities) and not surface.requires_receipts:
        return _blocked(surface, "MCP side-effect surfaces require receipts")
    if surface.stability == "experimental":
        return MCPExportDecision(
            status="review_required",
            allowed=False,
            reason="experimental MCP surfaces require compatibility review",
            surface_id=surface.id,
            required_controls=_required_controls(surface),
        )
    return MCPExportDecision(
        status="exportable",
        allowed=True,
        reason="stable MCP surface preserves capability, receipt, and secret boundaries",
        surface_id=surface.id,
        required_controls=_required_controls(surface),
    )


def _blocked(surface: MCPExportSurface, reason: str) -> MCPExportDecision:
    return MCPExportDecision(
        status="blocked",
        allowed=False,
        reason=reason,
        surface_id=surface.id,
        required_controls=_required_controls(surface),
    )


def _needs_receipts(capabilities: list[str]) -> bool:
    side_effect_prefixes = ("file.write", "shell.", "network.", "memory.write", "review.")
    return any(capability.startswith(side_effect_prefixes) for capability in capabilities)


def _required_controls(surface: MCPExportSurface) -> list[str]:
    controls = ["redaction"]
    if surface.capabilities:
        controls.append("capability_grants")
    if _needs_receipts(surface.capabilities):
        controls.append("receipts")
    if surface.docs_ref:
        controls.append("documented_contract")
    return controls
