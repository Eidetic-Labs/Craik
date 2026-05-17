"""Provider failover policy for routing decisions."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from craik.contracts.models import CraikModel

ProviderFailoverStatus = Literal["allowed", "denied", "stopped"]


class ProviderFailoverRule(CraikModel):
    """One explicit provider fallback rule."""

    from_provider_id: str
    to_provider_id: str
    reason: str
    requires_receipt: bool = True


class ProviderFailoverPolicy(CraikModel):
    """Failover policy for model/provider routing."""

    id: str
    rules: list[ProviderFailoverRule] = Field(default_factory=list)
    denied_provider_ids: list[str] = Field(default_factory=list)
    stop_reasons: list[str] = Field(default_factory=list)
    policy_envelope_id: str | None = None


class ProviderFailoverDecision(CraikModel):
    """Audit-ready provider failover decision."""

    status: ProviderFailoverStatus
    allowed: bool
    reason: str
    from_provider_id: str
    to_provider_id: str | None = None
    policy_envelope_id: str | None = None
    receipt_required: bool = True


def provider_failover_decision(
    *,
    policy: ProviderFailoverPolicy,
    from_provider_id: str,
    failure_reason: str,
) -> ProviderFailoverDecision:
    """Evaluate whether provider routing may fail over."""
    if failure_reason in policy.stop_reasons:
        return ProviderFailoverDecision(
            status="stopped",
            allowed=False,
            reason=f"failover stopped: {failure_reason}",
            from_provider_id=from_provider_id,
            policy_envelope_id=policy.policy_envelope_id,
        )
    for rule in policy.rules:
        if rule.from_provider_id != from_provider_id:
            continue
        if rule.to_provider_id in policy.denied_provider_ids:
            return ProviderFailoverDecision(
                status="denied",
                allowed=False,
                reason=f"fallback provider {rule.to_provider_id} is denied",
                from_provider_id=from_provider_id,
                to_provider_id=rule.to_provider_id,
                policy_envelope_id=policy.policy_envelope_id,
                receipt_required=rule.requires_receipt,
            )
        return ProviderFailoverDecision(
            status="allowed",
            allowed=True,
            reason=rule.reason,
            from_provider_id=from_provider_id,
            to_provider_id=rule.to_provider_id,
            policy_envelope_id=policy.policy_envelope_id,
            receipt_required=rule.requires_receipt,
        )
    return ProviderFailoverDecision(
        status="denied",
        allowed=False,
        reason=f"no failover rule for provider {from_provider_id}",
        from_provider_id=from_provider_id,
        policy_envelope_id=policy.policy_envelope_id,
    )
