from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from craik.runtime.auth.operator import OIDCAuthenticationError, OIDCAuthenticator, OIDCConfig

SECRET_B64URL = base64.urlsafe_b64encode(b"oidc-fuzz-secret").rstrip(b"=").decode("ascii")
VALID_ISSUER = "https://idp.example.test"


class _FuzzAuthenticator(OIDCAuthenticator):
    def __init__(self, *, jwks: dict[str, Any]) -> None:
        super().__init__(OIDCConfig(issuer=VALID_ISSUER, client_id="craik-cli"))
        self._fuzz_jwks = jwks

    def discovery(self) -> dict[str, Any]:
        return {
            "issuer": VALID_ISSUER,
            "authorization_endpoint": f"{VALID_ISSUER}/authorize",
            "device_authorization_endpoint": f"{VALID_ISSUER}/device",
            "token_endpoint": f"{VALID_ISSUER}/token",
            "jwks_uri": f"{VALID_ISSUER}/jwks",
        }

    def jwks(self) -> dict[str, Any]:
        return self._fuzz_jwks


json_scalar = st.none() | st.booleans() | st.integers() | st.floats(
    allow_nan=False,
    allow_infinity=False,
) | st.text(max_size=24)
json_value: st.SearchStrategy[Any] = st.recursive(
    json_scalar,
    lambda children: st.lists(children, max_size=4)
    | st.dictionaries(st.text(max_size=16), children, max_size=4),
    max_leaves=12,
)
json_object = st.dictionaries(st.text(max_size=16), json_value, max_size=8)
token_part_text = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters="."),
    max_size=64,
)


def test_valid_fuzz_harness_token_is_accepted() -> None:
    now = datetime.now(UTC)
    claims = {
        "iss": VALID_ISSUER,
        "aud": "craik-cli",
        "sub": "operator-123",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
    }
    token = _signed_hs256_token({"alg": "HS256", "kid": "fuzz-key"}, claims)
    authenticator = _FuzzAuthenticator(
        jwks={"keys": [{"kty": "oct", "kid": "fuzz-key", "k": SECRET_B64URL}]}
    )

    assert authenticator.validate_id_token(token)["sub"] == "operator-123"


@settings(max_examples=150, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    header=json_object,
    claims=json_object,
    signature=st.binary(max_size=96),
    jwks=json_value,
)
def test_validate_id_token_handles_json_jwt_and_jwks_shapes(
    header: dict[str, Any],
    claims: dict[str, Any],
    signature: bytes,
    jwks: Any,
) -> None:
    token = ".".join(
        [
            _json_part(header),
            _json_part(claims),
            _b64url(signature),
        ]
    )
    jwks_payload = jwks if isinstance(jwks, dict) else {"keys": jwks}

    _assert_only_oidc_error_escapes(token, jwks_payload)


@settings(max_examples=150, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    part_count=st.integers(min_value=0, max_value=6),
    parts=st.lists(token_part_text, min_size=0, max_size=6),
    jwks=json_object,
)
def test_validate_id_token_handles_arbitrary_compact_jwt_shapes(
    part_count: int,
    parts: list[str],
    jwks: dict[str, Any],
) -> None:
    while len(parts) < part_count:
        parts.append("")
    token = ".".join(parts[:part_count])

    _assert_only_oidc_error_escapes(token, jwks)


def _assert_only_oidc_error_escapes(token: str, jwks: dict[str, Any]) -> None:
    authenticator = _FuzzAuthenticator(jwks=jwks)
    try:
        authenticator.validate_id_token(token)
    except OIDCAuthenticationError:
        return


def _json_part(value: dict[str, Any]) -> str:
    return _b64url(json.dumps(value, sort_keys=True).encode("utf-8"))


def _signed_hs256_token(header: dict[str, Any], claims: dict[str, Any]) -> str:
    encoded_header = _json_part(header)
    encoded_claims = _json_part(claims)
    signing_input = f"{encoded_header}.{encoded_claims}".encode("ascii")
    signature = hmac.new(b"oidc-fuzz-secret", signing_input, hashlib.sha256).digest()
    return ".".join([encoded_header, encoded_claims, _b64url(signature)])


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")
