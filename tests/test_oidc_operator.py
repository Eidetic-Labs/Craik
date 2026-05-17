from __future__ import annotations

import base64
import hashlib
import hmac
import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib import parse

import pytest

from craik.runtime.auth.operator import (
    OIDCAuthenticationError,
    OIDCAuthenticator,
    OIDCConfig,
)

SECRET = b"oidc-test-secret"
KEY = {"kty": "oct", "kid": "test-key", "k": ""}
KEY["k"] = base64.urlsafe_b64encode(SECRET).rstrip(b"=").decode("ascii")


class _StubIdP:
    def __init__(self, *, jwks: dict[str, Any] | None = None) -> None:
        self.jwks = jwks or {"keys": [KEY]}
        self.server = HTTPServer(("127.0.0.1", 0), self._handler())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.issuer = f"http://127.0.0.1:{self.server.server_port}"
        self.seen_forms: list[dict[str, str]] = []

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=2)

    def token(self, **overrides: Any) -> str:
        now = datetime.now(UTC)
        claims: dict[str, Any] = {
            "iss": self.issuer,
            "aud": "craik-cli",
            "sub": "operator-123",
            "email": "operator@example.test",
            "name": "Test Operator",
            "groups": ["platform", "agents"],
            "jti": "token-1",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
        }
        claims.update(overrides)
        return _signed_jwt({"alg": "HS256", "kid": "test-key", "typ": "JWT"}, claims, SECRET)

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        parent = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                return

            def do_GET(self) -> None:
                if self.path == "/.well-known/openid-configuration":
                    _write_json(
                        self,
                        {
                            "issuer": parent.issuer,
                            "authorization_endpoint": f"{parent.issuer}/authorize",
                            "device_authorization_endpoint": f"{parent.issuer}/device",
                            "token_endpoint": f"{parent.issuer}/token",
                            "jwks_uri": f"{parent.issuer}/jwks",
                        },
                    )
                    return
                if self.path == "/jwks":
                    _write_json(self, parent.jwks)
                    return
                self.send_response(404)
                self.end_headers()

            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8")
                form = {key: values[0] for key, values in parse.parse_qs(raw).items()}
                parent.seen_forms.append(form)
                if self.path == "/device":
                    _write_json(
                        self,
                        {
                            "device_code": "device-code-1",
                            "user_code": "ABCD-EFGH",
                            "verification_uri": f"{parent.issuer}/activate",
                            "interval": 1,
                        },
                    )
                    return
                if self.path == "/token":
                    _write_json(
                        self,
                        {
                            "id_token": parent.token(),
                            "refresh_token": "refresh-token-value",
                            "token_type": "Bearer",
                        },
                    )
                    return
                self.send_response(404)
                self.end_headers()

        return Handler


@contextmanager
def _stub_idp(*, jwks: dict[str, Any] | None = None) -> Iterator[_StubIdP]:
    idp = _StubIdP(jwks=jwks)
    idp.start()
    try:
        yield idp
    finally:
        idp.stop()


def test_device_code_flow_returns_operator_session() -> None:
    with _stub_idp() as idp:
        authenticator = OIDCAuthenticator(
            OIDCConfig(issuer=idp.issuer, client_id="craik-cli"),
            timeout_seconds=1,
        )

        authorization = authenticator.device_authorization()
        session = authenticator.poll_device_token(
            authorization["device_code"],
            interval_seconds=1,
            max_wait_seconds=1,
        )

    assert session.subject == "operator-123"
    assert session.email == "operator@example.test"
    assert session.display_name == "Test Operator"
    assert session.groups == ["platform", "agents"]
    assert session.issuer == idp.issuer
    assert session.id_token_jti == "token-1"
    assert session.refresh_token_ref == "operator-session.refresh_token"
    assert idp.seen_forms[0]["client_id"] == "craik-cli"
    assert idp.seen_forms[1]["grant_type"] == "urn:ietf:params:oauth:grant-type:device_code"


def test_loopback_pkce_flow_exchanges_authorization_code() -> None:
    with _stub_idp() as idp:
        authenticator = OIDCAuthenticator(
            OIDCConfig(issuer=idp.issuer, client_id="craik-cli"),
            timeout_seconds=1,
        )

        authorization_url, verifier, state = authenticator.loopback_authorization_url(
            redirect_uri="http://127.0.0.1:8765/callback",
            state="state-1",
            code_verifier="verifier-1",
        )
        session = authenticator.exchange_authorization_code(
            code="code-1",
            redirect_uri="http://127.0.0.1:8765/callback",
            code_verifier=verifier,
        )

    parsed = parse.urlparse(authorization_url)
    query = parse.parse_qs(parsed.query)
    expected_challenge = _b64url(hashlib.sha256(b"verifier-1").digest())
    assert query["code_challenge"] == [expected_challenge]
    assert query["code_challenge_method"] == ["S256"]
    assert state == "state-1"
    assert session.subject == "operator-123"
    assert idp.seen_forms[-1]["grant_type"] == "authorization_code"
    assert idp.seen_forms[-1]["code_verifier"] == "verifier-1"


def test_tampered_id_token_is_rejected() -> None:
    with _stub_idp() as idp:
        authenticator = OIDCAuthenticator(OIDCConfig(issuer=idp.issuer, client_id="craik-cli"))
        token = idp.token()
        header, _claims, signature = token.split(".")
        tampered_claims = {
            "iss": idp.issuer,
            "aud": "craik-cli",
            "sub": "attacker",
            "iat": int(datetime.now(UTC).timestamp()),
            "exp": int((datetime.now(UTC) + timedelta(minutes=5)).timestamp()),
        }
        tampered = f"{header}.{_b64url(json.dumps(tampered_claims).encode('utf-8'))}.{signature}"

        with pytest.raises(OIDCAuthenticationError, match="signature"):
            authenticator.validate_id_token(tampered)


def test_alg_none_id_token_is_rejected() -> None:
    with _stub_idp() as idp:
        authenticator = OIDCAuthenticator(OIDCConfig(issuer=idp.issuer, client_id="craik-cli"))
        claims = {
            "iss": idp.issuer,
            "aud": "craik-cli",
            "sub": "operator-123",
            "iat": int(datetime.now(UTC).timestamp()),
            "exp": int((datetime.now(UTC) + timedelta(minutes=5)).timestamp()),
        }
        header = _b64url(json.dumps({"alg": "none", "kid": "test-key"}).encode("utf-8"))
        body = _b64url(json.dumps(claims).encode("utf-8"))
        token = f"{header}.{body}."

        with pytest.raises(OIDCAuthenticationError, match="unsupported algorithm"):
            authenticator.validate_id_token(token)


def test_unknown_kid_is_rejected() -> None:
    with _stub_idp() as idp:
        authenticator = OIDCAuthenticator(OIDCConfig(issuer=idp.issuer, client_id="craik-cli"))
        token = _signed_jwt(
            {"alg": "HS256", "kid": "unknown", "typ": "JWT"},
            {
                "iss": idp.issuer,
                "aud": "craik-cli",
                "sub": "operator-123",
                "iat": int(datetime.now(UTC).timestamp()),
                "exp": int((datetime.now(UTC) + timedelta(minutes=5)).timestamp()),
            },
            SECRET,
        )

        with pytest.raises(OIDCAuthenticationError, match="key id"):
            authenticator.validate_id_token(token)


def test_hs_token_with_asymmetric_jwks_key_is_rejected() -> None:
    rsa_jwks = {"keys": [{"kty": "RSA", "kid": "test-key", "n": "sXch", "e": "AQAB"}]}
    with _stub_idp(jwks=rsa_jwks) as idp:
        authenticator = OIDCAuthenticator(OIDCConfig(issuer=idp.issuer, client_id="craik-cli"))
        token = idp.token()

        with pytest.raises(OIDCAuthenticationError, match="incompatible"):
            authenticator.validate_id_token(token)


def _write_json(handler: BaseHTTPRequestHandler, payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _signed_jwt(header: dict[str, Any], claims: dict[str, Any], secret: bytes) -> str:
    encoded_header = _b64url(json.dumps(header, sort_keys=True).encode("utf-8"))
    encoded_claims = _b64url(json.dumps(claims, sort_keys=True).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_claims}".encode("ascii")
    signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_claims}.{_b64url(signature)}"


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")
