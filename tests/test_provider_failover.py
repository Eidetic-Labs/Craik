from craik.runtime.provider_failover import (
    ProviderFailoverPolicy,
    ProviderFailoverRule,
    provider_failover_decision,
)


def test_provider_failover_allows_configured_fallback() -> None:
    policy = ProviderFailoverPolicy(
        id="provider_failover_fixture",
        policy_envelope_id="policy_provider_fixture",
        rules=[
            ProviderFailoverRule(
                from_provider_id="provider_fixture_primary",
                to_provider_id="provider_fixture_fallback",
                reason="primary provider unavailable",
            )
        ],
    )

    decision = provider_failover_decision(
        policy=policy,
        from_provider_id="provider_fixture_primary",
        failure_reason="provider timeout",
    )

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.reason == "primary provider unavailable"
    assert decision.from_provider_id == "provider_fixture_primary"
    assert decision.to_provider_id == "provider_fixture_fallback"
    assert decision.policy_envelope_id == "policy_provider_fixture"
    assert decision.receipt_required is True


def test_provider_failover_denies_blocked_fallback_path() -> None:
    policy = ProviderFailoverPolicy(
        id="provider_failover_fixture",
        policy_envelope_id="policy_provider_fixture",
        denied_provider_ids=["provider_fixture_fallback"],
        rules=[
            ProviderFailoverRule(
                from_provider_id="provider_fixture_primary",
                to_provider_id="provider_fixture_fallback",
                reason="primary provider unavailable",
            )
        ],
    )

    decision = provider_failover_decision(
        policy=policy,
        from_provider_id="provider_fixture_primary",
        failure_reason="provider timeout",
    )

    assert decision.allowed is False
    assert decision.status == "denied"
    assert decision.reason == "fallback provider provider_fixture_fallback is denied"
    assert decision.to_provider_id == "provider_fixture_fallback"
    assert decision.policy_envelope_id == "policy_provider_fixture"
    assert decision.receipt_required is True


def test_provider_failover_stops_for_configured_failure_reason() -> None:
    policy = ProviderFailoverPolicy(
        id="provider_failover_fixture",
        policy_envelope_id="policy_provider_fixture",
        stop_reasons=["policy boundary mismatch"],
        rules=[
            ProviderFailoverRule(
                from_provider_id="provider_fixture_primary",
                to_provider_id="provider_fixture_fallback",
                reason="primary provider unavailable",
            )
        ],
    )

    decision = provider_failover_decision(
        policy=policy,
        from_provider_id="provider_fixture_primary",
        failure_reason="policy boundary mismatch",
    )

    assert decision.allowed is False
    assert decision.status == "stopped"
    assert decision.reason == "failover stopped: policy boundary mismatch"
    assert decision.to_provider_id is None
    assert decision.policy_envelope_id == "policy_provider_fixture"


def test_provider_failover_denies_missing_rule() -> None:
    policy = ProviderFailoverPolicy(
        id="provider_failover_fixture",
        policy_envelope_id="policy_provider_fixture",
    )

    decision = provider_failover_decision(
        policy=policy,
        from_provider_id="provider_fixture_primary",
        failure_reason="provider timeout",
    )

    assert decision.allowed is False
    assert decision.status == "denied"
    assert decision.reason == "no failover rule for provider provider_fixture_primary"
    assert decision.to_provider_id is None
    assert decision.policy_envelope_id == "policy_provider_fixture"
