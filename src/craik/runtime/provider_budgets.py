"""Provider budget and quota routing checks."""

from __future__ import annotations

from craik.contracts.models import CraikModel, ModelProvider


class ProviderBudgetStatus(CraikModel):
    """Non-secret budget and quota status for a provider routing decision."""

    provider_id: str
    budget_ref: str | None = None
    quota_ref: str | None = None
    budget_remaining: float | None = None
    quota_remaining: int | None = None
    blocked: bool = False
    reason: str | None = None


class ProviderRoutingBudgetDecision(CraikModel):
    """Budget-aware provider routing decision."""

    allowed: bool
    provider_id: str
    reason: str
    budget_ref: str | None = None
    quota_ref: str | None = None
    budget_remaining: float | None = None
    quota_remaining: int | None = None


def provider_budget_decision(
    provider: ModelProvider,
    status: ProviderBudgetStatus,
) -> ProviderRoutingBudgetDecision:
    """Return whether provider routing is allowed under current budget status."""
    if status.provider_id != provider.id:
        return ProviderRoutingBudgetDecision(
            allowed=False,
            provider_id=provider.id,
            reason=f"budget status is for {status.provider_id}, not {provider.id}",
            budget_ref=provider.budget_ref,
            quota_ref=provider.quota_ref,
        )
    if status.blocked:
        return _blocked(provider, status, status.reason or "provider budget status is blocked")
    if status.budget_remaining is not None and status.budget_remaining <= 0:
        return _blocked(provider, status, "provider budget is exhausted")
    if status.quota_remaining is not None and status.quota_remaining <= 0:
        return _blocked(provider, status, "provider quota is exhausted")
    return ProviderRoutingBudgetDecision(
        allowed=True,
        provider_id=provider.id,
        reason="provider budget and quota allow routing",
        budget_ref=provider.budget_ref,
        quota_ref=provider.quota_ref,
        budget_remaining=status.budget_remaining,
        quota_remaining=status.quota_remaining,
    )


def _blocked(
    provider: ModelProvider,
    status: ProviderBudgetStatus,
    reason: str,
) -> ProviderRoutingBudgetDecision:
    return ProviderRoutingBudgetDecision(
        allowed=False,
        provider_id=provider.id,
        reason=reason,
        budget_ref=provider.budget_ref,
        quota_ref=provider.quota_ref,
        budget_remaining=status.budget_remaining,
        quota_remaining=status.quota_remaining,
    )
