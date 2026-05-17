"""Desktop companion app posture decisions."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from craik.contracts.models import CraikModel

DesktopCompanionSupportLevel = Literal["supported", "experimental", "deferred"]
DesktopCompanionStatus = Literal["allowed", "review_required", "deferred", "blocked"]


class DesktopCompanionSurface(CraikModel):
    """Candidate desktop companion surface."""

    id: str
    support_level: DesktopCompanionSupportLevel
    operator_consent_required: bool = True
    preserves_policy_context: bool = True
    preserves_evidence_links: bool = True
    requires_receipts: bool = True
    local_storage_encrypted: bool = True
    stores_secrets: bool = False
    notification_controls: bool = True
    background_action_controls: bool = True
    docs_ref: str | None = None


class DesktopCompanionDecision(CraikModel):
    """Decision describing whether a desktop companion surface can be used."""

    status: DesktopCompanionStatus
    allowed: bool
    reason: str
    surface_id: str
    required_controls: list[str] = Field(default_factory=list)


def desktop_companion_decision(surface: DesktopCompanionSurface) -> DesktopCompanionDecision:
    """Evaluate desktop companion app posture."""
    if surface.stores_secrets:
        return _blocked(surface, "desktop companion surfaces must not store secrets")
    if not surface.operator_consent_required:
        return _blocked(surface, "desktop companion surfaces require operator consent")
    if not surface.local_storage_encrypted:
        return _blocked(surface, "desktop companion local storage must be encrypted")
    if not surface.notification_controls:
        return _blocked(surface, "desktop companion notifications require operator controls")
    if not surface.background_action_controls:
        return _blocked(surface, "desktop companion background actions require controls")
    if not surface.preserves_policy_context or not surface.preserves_evidence_links:
        return _blocked(
            surface,
            "desktop companion surfaces must preserve policy and evidence links",
        )
    if not surface.requires_receipts:
        return _blocked(surface, "desktop companion surfaces require receipts")
    if surface.support_level == "deferred":
        return DesktopCompanionDecision(
            status="deferred",
            allowed=False,
            reason="desktop companion surface is deferred by product posture",
            surface_id=surface.id,
            required_controls=_controls(surface),
        )
    if surface.support_level == "experimental":
        return DesktopCompanionDecision(
            status="review_required",
            allowed=False,
            reason="experimental desktop companion surfaces require explicit review",
            surface_id=surface.id,
            required_controls=_controls(surface),
        )
    return DesktopCompanionDecision(
        status="allowed",
        allowed=True,
        reason=(
            "desktop companion surface preserves consent, storage, notification, policy, "
            "evidence, and receipt controls"
        ),
        surface_id=surface.id,
        required_controls=_controls(surface),
    )


def _blocked(surface: DesktopCompanionSurface, reason: str) -> DesktopCompanionDecision:
    return DesktopCompanionDecision(
        status="blocked",
        allowed=False,
        reason=reason,
        surface_id=surface.id,
        required_controls=_controls(surface),
    )


def _controls(surface: DesktopCompanionSurface) -> list[str]:
    controls = ["operator_consent", "encrypted_local_storage", "notification_controls"]
    if surface.background_action_controls:
        controls.append("background_action_controls")
    if surface.preserves_policy_context:
        controls.append("policy_context")
    if surface.preserves_evidence_links:
        controls.append("evidence_links")
    if surface.requires_receipts:
        controls.append("receipts")
    if surface.docs_ref:
        controls.append("documented_decision")
    return controls
