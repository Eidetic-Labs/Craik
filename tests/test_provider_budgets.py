from craik.runtime.model_providers import (
    default_model_provider_registry,
    provider_selection_payload,
)
from craik.runtime.provider_budgets import ProviderBudgetStatus, provider_budget_decision


def _provider():
    return default_model_provider_registry().require("provider_fixture_local")


def test_provider_selection_includes_budget_and_quota_refs() -> None:
    payload = provider_selection_payload(_provider(), mode="chat")

    assert payload["budget_ref"] == "budget_fixture_monthly"
    assert payload["quota_ref"] == "quota_fixture_daily"


def test_provider_budget_decision_allows_remaining_budget_and_quota() -> None:
    decision = provider_budget_decision(
        _provider(),
        ProviderBudgetStatus(
            provider_id="provider_fixture_local",
            budget_ref="budget_fixture_monthly",
            quota_ref="quota_fixture_daily",
            budget_remaining=10.5,
            quota_remaining=20,
        ),
    )

    assert decision.allowed is True
    assert decision.reason == "provider budget and quota allow routing"
    assert decision.budget_remaining == 10.5
    assert decision.quota_remaining == 20


def test_provider_budget_decision_blocks_exhausted_budget() -> None:
    decision = provider_budget_decision(
        _provider(),
        ProviderBudgetStatus(
            provider_id="provider_fixture_local",
            budget_remaining=0,
            quota_remaining=20,
        ),
    )

    assert decision.allowed is False
    assert decision.reason == "provider budget is exhausted"


def test_provider_budget_decision_blocks_exhausted_quota() -> None:
    decision = provider_budget_decision(
        _provider(),
        ProviderBudgetStatus(
            provider_id="provider_fixture_local",
            budget_remaining=10,
            quota_remaining=0,
        ),
    )

    assert decision.allowed is False
    assert decision.reason == "provider quota is exhausted"


def test_provider_budget_decision_blocks_mismatched_status() -> None:
    decision = provider_budget_decision(
        _provider(),
        ProviderBudgetStatus(provider_id="other_provider", budget_remaining=10),
    )

    assert decision.allowed is False
    assert decision.reason == "budget status is for other_provider, not provider_fixture_local"


def test_provider_budget_decision_uses_explicit_block_reason() -> None:
    decision = provider_budget_decision(
        _provider(),
        ProviderBudgetStatus(
            provider_id="provider_fixture_local",
            blocked=True,
            reason="monthly spend approval required",
        ),
    )

    assert decision.allowed is False
    assert decision.reason == "monthly spend approval required"
