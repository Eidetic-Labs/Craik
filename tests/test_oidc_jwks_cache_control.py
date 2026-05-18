from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

from craik.runtime.auth.operator import OIDCAuthenticator, OIDCConfig


def test_jwks_cache_honors_cache_control_max_age() -> None:
    authenticator = _JWKSCacheAuthenticator({"Cache-Control": "max-age=1"})

    before = time.monotonic()
    first = authenticator.jwks()
    second = authenticator.jwks()

    assert first == second
    assert authenticator.fetch_count == 1
    assert 0 <= authenticator._jwks_expires_at - before <= 1.5


def test_jwks_cache_caps_max_age_to_configured_ttl() -> None:
    authenticator = _JWKSCacheAuthenticator(
        {"Cache-Control": "max-age=500"},
        discovery_ttl_seconds=100,
    )

    before = time.monotonic()
    authenticator.jwks()

    assert 0 <= authenticator._jwks_expires_at - before <= 100.5


def test_jwks_cache_refreshes_when_no_cache_is_present() -> None:
    authenticator = _JWKSCacheAuthenticator({"Cache-Control": "no-cache"})

    authenticator.jwks()
    authenticator.jwks()

    assert authenticator.fetch_count == 2


def test_jwks_cache_uses_configured_ttl_for_invalid_cache_control() -> None:
    authenticator = _JWKSCacheAuthenticator(
        {"Cache-Control": "max-age=not-an-int"},
        discovery_ttl_seconds=30,
    )

    before = time.monotonic()
    authenticator.jwks()

    assert 0 <= authenticator._jwks_expires_at - before <= 30.5


class _JWKSCacheAuthenticator(OIDCAuthenticator):
    def __init__(
        self,
        headers: Mapping[str, str],
        *,
        discovery_ttl_seconds: int = 3600,
    ) -> None:
        super().__init__(
            OIDCConfig(issuer="https://idp.example.test", client_id="craik-cli"),
            discovery_ttl_seconds=discovery_ttl_seconds,
        )
        self.headers = headers
        self.fetch_count = 0
        self._discovery = {
            "issuer": "https://idp.example.test",
            "jwks_uri": "https://idp.example.test/jwks",
        }
        self._discovery_expires_at = time.monotonic() + 3600

    def _get_json_with_headers(
        self,
        url: str,
    ) -> tuple[dict[str, Any], Mapping[str, str]]:
        assert url == "https://idp.example.test/jwks"
        self.fetch_count += 1
        return {"keys": [{"kty": "oct", "kid": "test-key", "k": "secret"}]}, self.headers
