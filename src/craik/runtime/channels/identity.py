"""Inbound channel identity pairing helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from craik.contracts.models import ChannelIdentityPairing, ChannelKind


def unpaired_channel_identity(
    *,
    pairing_id: str,
    channel: ChannelKind,
    external_id: str,
    service: str | None = None,
    display_name: str | None = None,
    created_at: datetime | None = None,
) -> ChannelIdentityPairing:
    """Create an unpaired external account record without authority."""
    now = created_at or datetime.now(UTC)
    return ChannelIdentityPairing.model_validate(
        {
            "id": pairing_id,
            "external_account": {
                "channel": channel,
                "external_id": external_id,
                "service": service,
                "display_name": display_name,
            },
            "status": "unpaired",
            "created_at": now,
            "updated_at": now,
        }
    )


def pair_channel_identity(
    pairing: ChannelIdentityPairing,
    *,
    subject: str,
    policy_envelope_id: str,
    paired_by: str,
    audit_id: str,
    paired_at: datetime | None = None,
) -> ChannelIdentityPairing:
    """Pair an external account to a Craik subject with audit and policy context."""
    now = paired_at or datetime.now(UTC)
    return pairing.model_copy(
        update={
            "status": "paired",
            "subject": subject,
            "policy_envelope_id": policy_envelope_id,
            "paired_at": now,
            "paired_by": paired_by,
            "audit_ids": [*pairing.audit_ids, audit_id],
            "updated_at": now,
        }
    )


def revoke_channel_identity(
    pairing: ChannelIdentityPairing,
    *,
    revoked_by: str,
    reason: str,
    audit_id: str,
    revoked_at: datetime | None = None,
) -> ChannelIdentityPairing:
    """Revoke a paired identity while preserving the pairing audit trail."""
    now = revoked_at or datetime.now(UTC)
    return pairing.model_copy(
        update={
            "status": "revoked",
            "revoked_at": now,
            "revoked_by": revoked_by,
            "revocation_reason": reason,
            "audit_ids": [*pairing.audit_ids, audit_id],
            "updated_at": now,
        }
    )


def allows_privileged_ingress(pairing: ChannelIdentityPairing) -> bool:
    """Return whether a channel identity can authorize privileged ingress."""
    return (
        pairing.status == "paired"
        and pairing.subject is not None
        and pairing.policy_envelope_id is not None
    )
