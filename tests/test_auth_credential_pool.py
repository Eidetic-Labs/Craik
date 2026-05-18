import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from craik.runtime.auth import (
    AuthProfile,
    AuthProfileStore,
    CredentialKind,
    CredentialPool,
    CredentialPoolConfig,
    CredentialPoolEntry,
)
from craik.runtime.providers.provider_transport import ProviderFamily


def _profile(profile_id: str) -> AuthProfile:
    family = profile_id.split(":", 1)[0]
    return AuthProfile(
        id=profile_id,
        kind=CredentialKind.API_KEY,
        provider_family=cast(ProviderFamily, family),
        metadata={"env_var": "TEST_API_KEY"},
        created_at=datetime(2026, 5, 17, tzinfo=UTC),
    )


def _seed_profiles(home: Path, *profile_ids: str) -> None:
    store = AuthProfileStore(home)
    for profile_id in profile_ids:
        store.put(_profile(profile_id))


def test_credential_pool_round_robin_distributes_evenly(tmp_path: Path) -> None:
    _seed_profiles(tmp_path, "openai:a", "openai:b")
    pool = CredentialPool(tmp_path)
    pool.put(
        CredentialPoolConfig(
            id="openai:default",
            provider_family="openai",
            strategy="round_robin",
            profiles=[
                CredentialPoolEntry(profile_id="openai:a"),
                CredentialPoolEntry(profile_id="openai:b"),
            ],
        )
    )

    selections = [pool.select("openai").id for _ in range(10)]

    assert selections.count("openai:a") == 5
    assert selections.count("openai:b") == 5


def test_credential_pool_failover_skips_rejected_profile(tmp_path: Path) -> None:
    _seed_profiles(tmp_path, "anthropic:a", "anthropic:b")
    pool = CredentialPool(tmp_path)
    pool.put(
        CredentialPoolConfig(
            id="anthropic:default",
            provider_family="anthropic",
            strategy="failover",
            profiles=[
                CredentialPoolEntry(profile_id="anthropic:a"),
                CredentialPoolEntry(profile_id="anthropic:b"),
            ],
        )
    )

    assert pool.select("anthropic").id == "anthropic:a"
    pool.report("anthropic:a", "rejected")

    assert pool.select("anthropic").id == "anthropic:b"


def test_credential_pool_concurrent_selects_advance_cursor_once(tmp_path: Path) -> None:
    _seed_profiles(tmp_path, "openai:a", "openai:b")
    pool = CredentialPool(tmp_path)
    pool.put(
        CredentialPoolConfig(
            id="openai:default",
            provider_family="openai",
            profiles=[
                CredentialPoolEntry(profile_id="openai:a"),
                CredentialPoolEntry(profile_id="openai:b"),
            ],
        )
    )
    barrier = threading.Barrier(2)
    selections: list[str] = []
    errors: list[Exception] = []

    def select_profile() -> None:
        try:
            barrier.wait(timeout=5)
            selections.append(CredentialPool(tmp_path).select("openai").id)
        except Exception as exc:  # pragma: no cover - assertion reports thread errors
            errors.append(exc)

    threads = [threading.Thread(target=select_profile) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert errors == []
    assert sorted(selections) == ["openai:a", "openai:b"]
