from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from craik.runtime.auth.operator import (
    OIDCAuthenticationError,
    OIDCAuthenticator,
    OIDCConfig,
)


def test_oidc_rejects_non_loopback_http_issuer_by_default() -> None:
    with pytest.raises(OIDCAuthenticationError, match="HTTPS"):
        OIDCAuthenticator(OIDCConfig(issuer="http://idp.example.com", client_id="craik-cli"))


def test_oidc_allows_loopback_http_when_explicitly_enabled() -> None:
    authenticator = OIDCAuthenticator(
        OIDCConfig(
            issuer="http://127.0.0.1:8443",
            client_id="craik-cli",
            oidc_allow_loopback_http=True,
        )
    )

    assert authenticator.config.issuer == "http://127.0.0.1:8443"


def test_oidc_rejects_http_jwks_from_https_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    authenticator = OIDCAuthenticator(
        OIDCConfig(issuer="https://idp.example.com", client_id="craik-cli")
    )

    def fake_get_json(url: str) -> dict[str, Any]:
        assert url == "https://idp.example.com/.well-known/openid-configuration"
        return {
            "issuer": "https://idp.example.com",
            "authorization_endpoint": "https://idp.example.com/authorize",
            "device_authorization_endpoint": "https://idp.example.com/device",
            "token_endpoint": "https://idp.example.com/token",
            "jwks_uri": "http://attacker.example.com/jwks",
        }

    monkeypatch.setattr(authenticator, "_get_json", fake_get_json)

    with pytest.raises(OIDCAuthenticationError, match="HTTPS"):
        authenticator.jwks()


def test_oidc_accepts_https_jwks_from_https_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    authenticator = OIDCAuthenticator(
        OIDCConfig(issuer="https://idp.example.com", client_id="craik-cli")
    )
    seen_urls: list[str] = []

    def fake_get_json(url: str) -> dict[str, Any]:
        seen_urls.append(url)
        if url.endswith("/.well-known/openid-configuration"):
            return {
                "issuer": "https://idp.example.com",
                "authorization_endpoint": "https://idp.example.com/authorize",
                "device_authorization_endpoint": "https://idp.example.com/device",
                "token_endpoint": "https://idp.example.com/token",
                "jwks_uri": "https://idp.example.com/jwks",
            }
        if url == "https://idp.example.com/jwks":
            return {"keys": []}
        raise AssertionError(f"unexpected URL: {url}")

    def fake_get_json_with_headers(url: str) -> tuple[dict[str, Any], Mapping[str, str]]:
        return fake_get_json(url), {}

    monkeypatch.setattr(authenticator, "_get_json", fake_get_json)
    monkeypatch.setattr(authenticator, "_get_json_with_headers", fake_get_json_with_headers)

    assert authenticator.jwks() == {"keys": []}
    assert seen_urls == [
        "https://idp.example.com/.well-known/openid-configuration",
        "https://idp.example.com/jwks",
    ]
