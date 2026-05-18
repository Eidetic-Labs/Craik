from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib import parse

import pytest

from craik.runtime.auth.sources import OIDCTokenExchangeSecretManager, SecretRefCredentialError
from craik.runtime.auth.sources.oidc_exchange import TOKEN_EXCHANGE_GRANT_TYPE
from craik.runtime.auth.workload import WorkloadIdentityError


def test_oidc_token_exchange_secret_manager_returns_and_caches_credential() -> None:
    workload = _StaticWorkloadIdentity("workload-token")
    with _stub_exchange() as exchange:
        manager = OIDCTokenExchangeSecretManager(
            workload_identity_provider=workload,
            exchange_endpoint=exchange.url,
            audience="craik-broker",
            target_token_type="urn:ietf:params:oauth:token-type:access_token",
            allow_loopback_http=True,
        )

        first = manager.resolve("provider/openai/work")
        second = manager.resolve("provider/openai/work")

    assert first == "exchanged-credential-1"
    assert second == "exchanged-credential-1"
    assert exchange.requests == [
        {
            "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
            "subject_token": "workload-token",
            "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
            "audience": "craik-broker",
            "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "resource": "provider/openai/work",
        }
    ]


def test_oidc_token_exchange_secret_manager_refreshes_on_expiry() -> None:
    workload = _StaticWorkloadIdentity("workload-token")
    with _stub_exchange(expires_in=1) as exchange:
        manager = OIDCTokenExchangeSecretManager(
            workload_identity_provider=workload,
            exchange_endpoint=exchange.url,
            audience="craik-broker",
            target_token_type="urn:ietf:params:oauth:token-type:access_token",
            safety_margin_seconds=2,
            allow_loopback_http=True,
        )

        first = manager.resolve("provider/openai/work")
        second = manager.resolve("provider/openai/work")

    assert first == "exchanged-credential-1"
    assert second == "exchanged-credential-2"
    assert len(exchange.requests) == 2


def test_oidc_token_exchange_secret_manager_fails_when_workload_token_unavailable() -> None:
    manager = OIDCTokenExchangeSecretManager(
        workload_identity_provider=_FailingWorkloadIdentity(),
        exchange_endpoint="http://127.0.0.1:9/exchange",
        audience="craik-broker",
        target_token_type="urn:ietf:params:oauth:token-type:access_token",
        allow_loopback_http=True,
    )

    with pytest.raises(SecretRefCredentialError) as error:
        manager.resolve("provider/openai/work")

    assert "workload-secret" not in str(error.value)
    assert "provider/openai/work" not in str(error.value)


class _StaticWorkloadIdentity:
    def __init__(self, token: str) -> None:
        self.token = token

    def get_token(self, audience: str) -> str:
        assert audience == "craik-broker"
        return self.token


class _FailingWorkloadIdentity:
    def get_token(self, audience: str) -> str:
        del audience
        raise WorkloadIdentityError("workload identity unavailable")


class _StubExchange:
    def __init__(self, *, expires_in: int = 300) -> None:
        self.expires_in = expires_in
        self.requests: list[dict[str, str]] = []
        self.server = HTTPServer(("127.0.0.1", 0), self._handler())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.url = f"http://127.0.0.1:{self.server.server_port}/exchange"

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=2)

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        parent = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                return

            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8")
                form = {key: values[0] for key, values in parse.parse_qs(raw).items()}
                parent.requests.append(form)
                _write_json(
                    self,
                    {
                        "access_token": f"exchanged-credential-{len(parent.requests)}",
                        "expires_in": parent.expires_in,
                        "issued_token_type": form["requested_token_type"],
                        "token_type": "Bearer",
                    },
                )

        return Handler


@contextmanager
def _stub_exchange(*, expires_in: int = 300) -> Iterator[_StubExchange]:
    exchange = _StubExchange(expires_in=expires_in)
    exchange.start()
    try:
        yield exchange
    finally:
        exchange.stop()


def _write_json(handler: BaseHTTPRequestHandler, payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
