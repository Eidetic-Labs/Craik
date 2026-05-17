"""Tool result attestation and knowledge freshness helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from craik.contracts.models import (
    FreshnessProbeStatus,
    KnowledgeFreshnessProbe,
    ToolResultAttestation,
)


def attestation_is_fresh(
    attestation: ToolResultAttestation | None,
    *,
    now: datetime | None = None,
) -> bool:
    """Return whether an attestation exists and has not expired."""
    if attestation is None or attestation.status != "attested":
        return False
    if attestation.expires_at is None:
        return True
    return attestation.expires_at > (now or datetime.now(UTC))


def classify_probe(
    probe: KnowledgeFreshnessProbe,
    *,
    now: datetime | None = None,
    expiring_within: timedelta = timedelta(hours=1),
) -> FreshnessProbeStatus:
    """Classify a freshness probe relative to the current time."""
    current = now or datetime.now(UTC)
    if probe.status == "missing" or probe.captured_at is None:
        return "missing"
    if probe.expires_at is None:
        return "fresh"
    if probe.expires_at <= current:
        return "expired"
    if probe.expires_at <= current + expiring_within:
        return "expiring"
    return "fresh"


def stale_risk_warnings(
    probes: list[KnowledgeFreshnessProbe],
    *,
    now: datetime | None = None,
) -> list[str]:
    """Return stale-risk warnings for expiring, expired, or missing probes."""
    warnings: list[str] = []
    for probe in sorted(probes, key=lambda item: item.id):
        status = classify_probe(probe, now=now)
        if status in {"expiring", "expired", "missing"}:
            warnings.append(
                probe.stale_risk_warning
                or f"Freshness probe {probe.id} for {probe.target} is {status}."
            )
    return warnings


def missing_attestation_warning(
    *,
    expected_attestation_id: str,
    attestations: list[ToolResultAttestation],
) -> str | None:
    """Return a stale-risk warning when an expected attestation is absent."""
    if any(attestation.id == expected_attestation_id for attestation in attestations):
        return None
    return f"Missing tool result attestation: {expected_attestation_id}."
