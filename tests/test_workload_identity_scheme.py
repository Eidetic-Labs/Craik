from __future__ import annotations

import json
from typing import Any

import pytest

import craik.runtime.auth.sources.oidc_exchange as oidc_exchange
import craik.runtime.auth.workload.oidc_federation as oidc_federation
from craik.runtime.auth.sources import OIDCTokenExchangeSecretManager, SecretRefCredentialError
from craik.runtime.auth.workload import (
    GenericFileTokenIdentity,
    GitHubActionsWorkloadIdentity,
    WorkloadIdentityError,
)


def test_github_actions_workload_identity_accepts_https_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_urls: list[str] = []

    def fake_urlopen(http_request: Any, *, timeout: float) -> _Response:
        del timeout
        seen_urls.append(http_request.full_url)
        return _Response({"value": "github-token"})

    monkeypatch.setattr(oidc_federation.request, "urlopen", fake_urlopen)
    provider = GitHubActionsWorkloadIdentity(
        env={
            "ACTIONS_ID_TOKEN_REQUEST_URL": "https://token.actions.example/oidc",
            "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "request-token",
        },
    )

    assert provider.get_token("craik-broker") == "github-token"
    assert seen_urls == ["https://token.actions.example/oidc?audience=craik-broker"]


def test_github_actions_workload_identity_rejects_http_endpoint() -> None:
    provider = GitHubActionsWorkloadIdentity(
        env={
            "ACTIONS_ID_TOKEN_REQUEST_URL": "http://attacker.example.com/oidc",
            "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "request-token",
        },
    )

    with pytest.raises(WorkloadIdentityError, match="HTTPS"):
        provider.get_token("craik-broker")


def test_oidc_token_exchange_rejects_http_endpoint() -> None:
    with pytest.raises(SecretRefCredentialError, match="HTTPS"):
        OIDCTokenExchangeSecretManager(
            workload_identity_provider=_StaticWorkloadIdentity(),
            exchange_endpoint="http://exchange.example.com/token",
            audience="craik-broker",
            target_token_type="urn:ietf:params:oauth:token-type:access_token",
        )


def test_oidc_token_exchange_accepts_https_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    seen_urls: list[str] = []

    def fake_urlopen(http_request: Any, *, timeout: float) -> _Response:
        del timeout
        seen_urls.append(http_request.full_url)
        return _Response({"access_token": "exchanged-token", "expires_in": 300})

    monkeypatch.setattr(oidc_exchange.request, "urlopen", fake_urlopen)
    manager = OIDCTokenExchangeSecretManager(
        workload_identity_provider=_StaticWorkloadIdentity(),
        exchange_endpoint="https://broker.example.com/token",
        audience="craik-broker",
        target_token_type="urn:ietf:params:oauth:token-type:access_token",
    )

    assert manager.resolve("provider/openai/work") == "exchanged-token"
    assert seen_urls == ["https://broker.example.com/token"]


def test_file_workload_identity_rejects_symlink(tmp_path: Any) -> None:
    target = tmp_path / "target-token"
    target.write_text("token\n", encoding="utf-8")
    target.chmod(0o600)
    link = tmp_path / "token"
    link.symlink_to(target)

    with pytest.raises(WorkloadIdentityError, match="could not be read"):
        GenericFileTokenIdentity(path=link).get_token("audience")


def test_file_workload_identity_rejects_group_readable_file(tmp_path: Any) -> None:
    token = tmp_path / "token"
    token.write_text("token\n", encoding="utf-8")
    token.chmod(0o640)

    with pytest.raises(WorkloadIdentityError, match="could not be read"):
        GenericFileTokenIdentity(path=token).get_token("audience")


class _Response:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class _StaticWorkloadIdentity:
    def get_token(self, audience: str) -> str:
        assert audience == "craik-broker"
        return "workload-token"
