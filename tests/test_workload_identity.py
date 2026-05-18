from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib import parse

import pytest

from craik.runtime.auth.workload import (
    EnvVarTokenIdentity,
    GenericFileTokenIdentity,
    GitHubActionsWorkloadIdentity,
    KubernetesProjectedTokenIdentity,
    WorkloadIdentityError,
    WorkloadIdentityProvider,
)

_THREAD_JOIN_TIMEOUT_SECONDS = 2


def test_github_actions_workload_identity_requests_audience_token() -> None:
    with _stub_oidc_endpoint() as endpoint:
        provider = GitHubActionsWorkloadIdentity(
            env={
                "ACTIONS_ID_TOKEN_REQUEST_URL": endpoint.url,
                "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "request-token",
            },
            timeout_seconds=1,
            allow_loopback_http=True,
        )

        token = provider.get_token("craik-broker")

    assert token == "github-oidc-token"
    assert endpoint.seen_authorization == ["Bearer request-token"]
    assert endpoint.seen_audiences == ["craik-broker"]


def test_workload_identity_provider_protocol_default_raises_not_implemented() -> None:
    class IncompleteWorkloadIdentityProvider(WorkloadIdentityProvider):
        pass

    provider = IncompleteWorkloadIdentityProvider()

    with pytest.raises(NotImplementedError):
        provider.get_token("audience")


def test_github_actions_workload_identity_fails_outside_actions() -> None:
    provider = GitHubActionsWorkloadIdentity(env={})

    with pytest.raises(WorkloadIdentityError, match="GitHub Actions OIDC environment"):
        provider.get_token("audience")


def test_generic_file_token_identity_refreshes_before_expiry(tmp_path: Path) -> None:
    token_path = tmp_path / "token"
    token_path.write_text("token-1\n", encoding="utf-8")
    token_path.chmod(0o600)
    provider = GenericFileTokenIdentity(
        path=token_path,
        ttl_seconds=1,
        refresh_margin_seconds=2,
    )

    assert provider.get_token("audience") == "token-1"
    token_path.write_text("token-2\n", encoding="utf-8")
    token_path.chmod(0o600)
    assert provider.get_token("audience") == "token-2"


def test_kubernetes_projected_token_identity_reads_configured_path(tmp_path: Path) -> None:
    token_path = tmp_path / "kubernetes-token"
    token_path.write_text("kubernetes-token\n", encoding="utf-8")
    token_path.chmod(0o600)

    token = KubernetesProjectedTokenIdentity(path=token_path).get_token("cluster-audience")

    assert token == "kubernetes-token"


def test_env_var_token_identity_refreshes_before_expiry() -> None:
    env = {"WORKLOAD_TOKEN": "token-1"}
    provider = EnvVarTokenIdentity(
        env_var="WORKLOAD_TOKEN",
        env=env,
        ttl_seconds=1,
        refresh_margin_seconds=2,
    )

    assert provider.get_token("audience") == "token-1"
    env["WORKLOAD_TOKEN"] = "token-2"
    assert provider.get_token("audience") == "token-2"


def test_workload_identity_errors_do_not_include_token_material(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing-token"
    provider = GenericFileTokenIdentity(path=missing_path)

    with pytest.raises(WorkloadIdentityError) as error:
        provider.get_token("audience")

    assert "token-secret" not in str(error.value)
    assert str(missing_path) not in str(error.value)


class _StubOIDCEndpoint:
    def __init__(self) -> None:
        self.server = HTTPServer(("127.0.0.1", 0), self._handler())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.url = f"http://127.0.0.1:{self.server.server_port}/oidc"
        self.seen_authorization: list[str] = []
        self.seen_audiences: list[str] = []

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=_THREAD_JOIN_TIMEOUT_SECONDS)

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        parent = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                # Intentionally suppress HTTP request logging in tests.
                pass

            def do_GET(self) -> None:
                parsed = parse.urlparse(self.path)
                query = parse.parse_qs(parsed.query)
                parent.seen_authorization.append(self.headers.get("Authorization", ""))
                parent.seen_audiences.append(query.get("audience", [""])[0])
                _write_json(self, {"value": "github-oidc-token"})

        return Handler


@contextmanager
def _stub_oidc_endpoint() -> Iterator[_StubOIDCEndpoint]:
    endpoint = _StubOIDCEndpoint()
    endpoint.start()
    try:
        yield endpoint
    finally:
        endpoint.stop()


def _write_json(handler: BaseHTTPRequestHandler, payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
