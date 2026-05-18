from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from craik.runtime.auth.operator import OIDCAuthenticator, OIDCConfig, OperatorSession
from craik.runtime.auth.operator.oidc import OIDCAuthenticationError


def test_authorization_code_exchange_accepts_matching_state() -> None:
    authenticator = _StateValidationAuthenticator()

    session = authenticator.exchange_authorization_code(
        code="code-1",
        redirect_uri="http://127.0.0.1:8765/callback",
        code_verifier="verifier-1",
        expected_state="state-1",
        received_state="state-1",
    )

    assert session.subject == "operator-123"
    assert authenticator.exchanged is True


def test_authorization_code_exchange_rejects_mismatched_state_before_token_request() -> None:
    authenticator = _StateValidationAuthenticator()

    with pytest.raises(OIDCAuthenticationError, match="state did not match"):
        authenticator.exchange_authorization_code(
            code="code-1",
            redirect_uri="http://127.0.0.1:8765/callback",
            code_verifier="verifier-1",
            expected_state="state-1",
            received_state="state-2",
        )

    assert authenticator.exchanged is False


def test_authorization_code_exchange_rejects_missing_state_before_token_request() -> None:
    authenticator = _StateValidationAuthenticator()

    with pytest.raises(OIDCAuthenticationError, match="state did not match"):
        authenticator.exchange_authorization_code(
            code="code-1",
            redirect_uri="http://127.0.0.1:8765/callback",
            code_verifier="verifier-1",
            expected_state="state-1",
            received_state=None,
        )

    assert authenticator.exchanged is False


def test_authorization_code_exchange_rejects_empty_expected_state_with_received_state() -> None:
    authenticator = _StateValidationAuthenticator()

    with pytest.raises(OIDCAuthenticationError, match="state did not match"):
        authenticator.exchange_authorization_code(
            code="code-1",
            redirect_uri="http://127.0.0.1:8765/callback",
            code_verifier="verifier-1",
            expected_state="",
            received_state="state-2",
        )

    assert authenticator.exchanged is False


class _StateValidationAuthenticator(OIDCAuthenticator):
    def __init__(self) -> None:
        super().__init__(
            OIDCConfig(issuer="https://idp.example.test", client_id="craik-cli"),
            timeout_seconds=1,
        )
        self.exchanged = False

    def _discovery_endpoint(self, key: str) -> str:
        assert key == "token_endpoint"
        return "https://idp.example.test/oauth/token"

    def _post_form(
        self,
        url: str,
        payload: dict[str, str],
        *,
        allow_oauth_error: bool = False,
    ) -> dict[str, Any]:
        self.exchanged = True
        assert url == "https://idp.example.test/oauth/token"
        assert payload["grant_type"] == "authorization_code"
        return {"id_token": "not-used"}

    def session_from_token_response(self, payload: dict[str, Any]) -> OperatorSession:
        return OperatorSession(
            subject="operator-123",
            email="operator@example.test",
            display_name="Test Operator",
            groups=["platform"],
            issuer="https://idp.example.test",
            id_token_jti="token-1",
            expires_at=datetime(2030, 1, 1, tzinfo=UTC),
            refresh_token_ref=None,
        )
