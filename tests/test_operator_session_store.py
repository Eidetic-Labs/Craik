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
from pathlib import Path
from typing import Any, cast
from urllib import parse

from typer.testing import CliRunner

from craik.cli import app
from craik.runtime.auth.operator import (
    OIDCAuthenticator,
    OperatorSession,
    OperatorSessionNotFoundError,
    OperatorSessionStore,
    operator_session_store_owner_only,
)

SECRET = b"operator-session-secret"
KEY = {
    "kty": "oct",
    "kid": "session-key",
    "k": base64.urlsafe_b64encode(SECRET).rstrip(b"=").decode("ascii"),
}

runner = CliRunner()


def test_operator_session_store_round_trips_and_supports_concurrent_reads(
    tmp_path: Path,
) -> None:
    store = OperatorSessionStore(tmp_path)
    session = _session()

    store.put(session, refresh_token="refresh-token")
    seen: list[str] = []
    threads = [threading.Thread(target=lambda: seen.append(store.get().subject)) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert store.get() == session
    assert seen == ["operator-123"] * 8
    assert operator_session_store_owner_only(store.path)


def test_operator_session_store_refreshes_near_expiry(tmp_path: Path) -> None:
    store = OperatorSessionStore(tmp_path)
    expired = _session(expires_at=datetime.now(UTC) + timedelta(seconds=30))
    refreshed = _session(subject="operator-456", expires_at=datetime.now(UTC) + timedelta(hours=1))
    authenticator = _RefreshAuthenticator(refreshed)
    store.put(expired, refresh_token="old-refresh")

    result = store.get(authenticator=cast(OIDCAuthenticator, authenticator))

    assert result.subject == "operator-456"
    assert store.get().subject == "operator-456"
    assert authenticator.refresh_seen == ["old-refresh"]


def test_operator_session_store_logout_revokes_and_removes_session(tmp_path: Path) -> None:
    store = OperatorSessionStore(tmp_path)
    store.put(_session(), refresh_token="refresh-token")
    authenticator = _RefreshAuthenticator(_session())

    revoked = store.delete(authenticator=cast(OIDCAuthenticator, authenticator))

    assert revoked is True
    assert authenticator.revoked_seen == ["refresh-token"]
    try:
        store.get()
    except OperatorSessionNotFoundError:
        pass
    else:
        raise AssertionError("expected missing session after logout")


def test_operator_login_whoami_logout_cli_against_stub_idp(tmp_path: Path) -> None:
    home = tmp_path / "home"
    env = {"CRAIK_HOME": str(home), "CRAIK_OIDC_ALLOW_LOOPBACK_HTTP": "1"}
    with _stub_idp() as idp:
        login = runner.invoke(
            app,
            [
                "login",
                "--issuer",
                idp.issuer,
                "--client-id",
                "craik-cli",
                "--max-wait-seconds",
                "1",
            ],
            env=env,
        )
        whoami = runner.invoke(app, ["whoami"], env=env)
        logout = runner.invoke(
            app,
            ["logout", "--issuer", idp.issuer, "--client-id", "craik-cli"],
            env=env,
        )

    assert login.exit_code == 0, login.stdout
    assert whoami.exit_code == 0, whoami.stdout
    assert logout.exit_code == 0, logout.stdout
    assert json.loads(whoami.stdout)["subject"] == "operator-123"
    assert json.loads(logout.stdout) == {"logged_out": True, "revoked": True}
    assert idp.revocations == ["refresh-token-value"]


class _RefreshAuthenticator:
    def __init__(self, session: OperatorSession) -> None:
        self.session = session
        self.refresh_seen: list[str] = []
        self.revoked_seen: list[str] = []

    def refresh_session(self, refresh_token: str) -> tuple[OperatorSession, str]:
        self.refresh_seen.append(refresh_token)
        return self.session, "new-refresh"

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        self.revoked_seen.append(refresh_token)
        return True


class _StubIdP:
    def __init__(self) -> None:
        self.server = HTTPServer(("127.0.0.1", 0), self._handler())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.issuer = f"http://127.0.0.1:{self.server.server_port}"
        self.revocations: list[str] = []

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=2)

    def token(self) -> str:
        now = datetime.now(UTC)
        return _signed_jwt(
            {"alg": "HS256", "kid": "session-key", "typ": "JWT"},
            {
                "iss": self.issuer,
                "aud": "craik-cli",
                "sub": "operator-123",
                "email": "operator@example.test",
                "groups": ["platform"],
                "jti": "session-token",
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(minutes=10)).timestamp()),
            },
            SECRET,
        )

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
                            "revocation_endpoint": f"{parent.issuer}/revoke",
                            "jwks_uri": f"{parent.issuer}/jwks",
                        },
                    )
                    return
                if self.path == "/jwks":
                    _write_json(self, {"keys": [KEY]})
                    return
                self.send_response(404)
                self.end_headers()

            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8")
                form = {key: values[0] for key, values in parse.parse_qs(raw).items()}
                if self.path == "/device":
                    _write_json(
                        self,
                        {
                            "device_code": "device-code",
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
                if self.path == "/revoke":
                    parent.revocations.append(form["token"])
                    _write_json(self, {"revoked": True})
                    return
                self.send_response(404)
                self.end_headers()

        return Handler


@contextmanager
def _stub_idp() -> Iterator[_StubIdP]:
    idp = _StubIdP()
    idp.start()
    try:
        yield idp
    finally:
        idp.stop()


def _session(
    *,
    subject: str = "operator-123",
    expires_at: datetime | None = None,
) -> OperatorSession:
    return OperatorSession(
        subject=subject,
        email="operator@example.test",
        display_name="Operator",
        groups=["platform"],
        issuer="https://issuer.example.test",
        id_token_jti="token-1",
        expires_at=expires_at or datetime.now(UTC) + timedelta(hours=1),
        refresh_token_ref="operator-session.refresh_token",
    )


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
