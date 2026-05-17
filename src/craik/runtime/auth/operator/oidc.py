"""OIDC operator authentication and ID token validation."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib import error, parse, request

from pydantic import Field

from craik.contracts.models import CraikModel
from craik.runtime.auth.operator.session import OperatorSession

DEFAULT_DISCOVERY_TTL_SECONDS = 3600
DEFAULT_CLOCK_SKEW_SECONDS = 60
RSA_SHA256_DIGEST_INFO = bytes.fromhex("3031300d060960864801650304020105000420")


class OIDCAuthenticationError(RuntimeError):
    """Raised when OIDC authentication or token validation fails."""


class OIDCConfig(CraikModel):
    """OIDC client configuration for an operator identity provider."""

    issuer: str
    client_id: str
    client_secret_ref: str | None = None
    scopes: list[str] = Field(default_factory=lambda: ["openid", "profile", "email"])
    audience: str | None = None
    groups_claim: str = "groups"


@dataclass
class OIDCAuthenticator:
    """Authenticate operators through a configured OIDC provider."""

    config: OIDCConfig
    timeout_seconds: float = 5.0
    discovery_ttl_seconds: int = DEFAULT_DISCOVERY_TTL_SECONDS
    clock_skew_seconds: int = DEFAULT_CLOCK_SKEW_SECONDS
    _discovery: dict[str, Any] | None = field(default=None, init=False)
    _discovery_expires_at: float = field(default=0.0, init=False)
    _jwks: dict[str, Any] | None = field(default=None, init=False)
    _jwks_expires_at: float = field(default=0.0, init=False)

    def device_authorization(self) -> dict[str, Any]:
        """Start RFC 8628 device-code authorization."""
        endpoint = _string_endpoint(self.discovery(), "device_authorization_endpoint")
        payload = {
            "client_id": self.config.client_id,
            "scope": " ".join(self.config.scopes),
        }
        if self.config.audience:
            payload["audience"] = self.config.audience
        return self._post_form(endpoint, payload)

    def poll_device_token(
        self,
        device_code: str,
        *,
        interval_seconds: int = 5,
        max_wait_seconds: int = 600,
    ) -> OperatorSession:
        """Poll the token endpoint until the device-code flow completes."""
        endpoint = _string_endpoint(self.discovery(), "token_endpoint")
        deadline = time.monotonic() + max_wait_seconds
        interval = max(1, interval_seconds)
        while time.monotonic() <= deadline:
            payload = {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
                "client_id": self.config.client_id,
            }
            response = self._post_form(endpoint, payload, allow_oauth_error=True)
            if "id_token" in response:
                return self.session_from_token_response(response)
            oauth_error = response.get("error")
            if oauth_error == "authorization_pending":
                time.sleep(interval)
                continue
            if oauth_error == "slow_down":
                interval += 5
                time.sleep(interval)
                continue
            raise OIDCAuthenticationError("device-code authorization failed")
        raise OIDCAuthenticationError("device-code authorization timed out")

    def loopback_authorization_url(
        self,
        *,
        redirect_uri: str,
        state: str | None = None,
        code_verifier: str | None = None,
    ) -> tuple[str, str, str]:
        """Build a loopback authorization URL with PKCE parameters."""
        verifier = code_verifier or _pkce_verifier()
        challenge = _b64url(hashlib.sha256(verifier.encode("ascii")).digest())
        session_state = state or secrets.token_urlsafe(24)
        endpoint = _string_endpoint(self.discovery(), "authorization_endpoint")
        query = parse.urlencode(
            {
                "response_type": "code",
                "client_id": self.config.client_id,
                "redirect_uri": redirect_uri,
                "scope": " ".join(self.config.scopes),
                "state": session_state,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            }
        )
        return f"{endpoint}?{query}", verifier, session_state

    def exchange_authorization_code(
        self,
        *,
        code: str,
        redirect_uri: str,
        code_verifier: str,
    ) -> OperatorSession:
        """Exchange a loopback authorization code for an operator session."""
        endpoint = _string_endpoint(self.discovery(), "token_endpoint")
        response = self._post_form(
            endpoint,
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": self.config.client_id,
                "code_verifier": code_verifier,
            },
        )
        return self.session_from_token_response(response)

    def session_from_token_response(self, payload: dict[str, Any]) -> OperatorSession:
        """Validate an ID token response and return a normalized session."""
        id_token = payload.get("id_token")
        if not isinstance(id_token, str):
            raise OIDCAuthenticationError("OIDC token response did not include an ID token")
        claims = self.validate_id_token(id_token)
        refresh_token_ref = "token_response.refresh_token" if payload.get("refresh_token") else None
        return OperatorSession(
            subject=_required_string(claims, "sub"),
            email=_optional_string(claims, "email"),
            display_name=_optional_string(claims, "name"),
            groups=_groups_from_claim(claims.get(self.config.groups_claim)),
            issuer=_required_string(claims, "iss"),
            id_token_jti=_token_identifier(claims),
            expires_at=_timestamp_claim(claims, "exp"),
            refresh_token_ref=refresh_token_ref,
        )

    def validate_id_token(self, token: str) -> dict[str, Any]:
        """Validate an OIDC ID token against discovery metadata and JWKS."""
        header, claims, signing_input, signature = _decode_jwt(token)
        alg = _required_string(header, "alg")
        if alg == "none":
            raise OIDCAuthenticationError("OIDC ID token uses an unsupported algorithm")
        kid = _required_string(header, "kid")
        key = self._jwk_for_kid(kid)
        _verify_signature(alg, key, signing_input, signature)
        self._validate_claims(claims)
        return claims

    def discovery(self) -> dict[str, Any]:
        """Return cached OIDC discovery metadata."""
        now = time.monotonic()
        if self._discovery is not None and now < self._discovery_expires_at:
            return self._discovery
        url = self.config.issuer.rstrip("/") + "/.well-known/openid-configuration"
        payload = self._get_json(url)
        issuer = payload.get("issuer")
        if issuer != self.config.issuer.rstrip("/"):
            raise OIDCAuthenticationError("OIDC discovery issuer did not match configuration")
        self._discovery = payload
        self._discovery_expires_at = now + self.discovery_ttl_seconds
        return payload

    def jwks(self) -> dict[str, Any]:
        """Return cached JWKS metadata."""
        now = time.monotonic()
        if self._jwks is not None and now < self._jwks_expires_at:
            return self._jwks
        payload = self._get_json(_string_endpoint(self.discovery(), "jwks_uri"))
        keys = payload.get("keys")
        if not isinstance(keys, list):
            raise OIDCAuthenticationError("OIDC JWKS did not contain keys")
        self._jwks = payload
        self._jwks_expires_at = now + self.discovery_ttl_seconds
        return payload

    def _validate_claims(self, claims: dict[str, Any]) -> None:
        if claims.get("iss") != self.config.issuer.rstrip("/"):
            raise OIDCAuthenticationError("OIDC ID token issuer did not match configuration")
        audience = claims.get("aud")
        audiences = audience if isinstance(audience, list) else [audience]
        if self.config.client_id not in audiences and self.config.audience not in audiences:
            raise OIDCAuthenticationError("OIDC ID token audience did not match configuration")
        now = datetime.now(UTC)
        skew = timedelta(seconds=self.clock_skew_seconds)
        if _timestamp_claim(claims, "exp") < now - skew:
            raise OIDCAuthenticationError("OIDC ID token is expired")
        nbf = _optional_timestamp_claim(claims, "nbf")
        if nbf is not None and nbf > now + skew:
            raise OIDCAuthenticationError("OIDC ID token is not yet valid")
        iat = _optional_timestamp_claim(claims, "iat")
        if iat is not None and iat > now + skew:
            raise OIDCAuthenticationError("OIDC ID token was issued in the future")
        _required_string(claims, "sub")

    def _jwk_for_kid(self, kid: str) -> dict[str, Any]:
        for key in self.jwks()["keys"]:
            if isinstance(key, dict) and key.get("kid") == kid:
                return key
        raise OIDCAuthenticationError("OIDC ID token key id was not found in JWKS")

    def _get_json(self, url: str) -> dict[str, Any]:
        http_request = request.Request(url, method="GET")
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                return _json_response(response.read())
        except (TimeoutError, error.URLError) as exc:
            raise OIDCAuthenticationError("OIDC endpoint request failed") from exc

    def _post_form(
        self,
        url: str,
        payload: dict[str, str],
        *,
        allow_oauth_error: bool = False,
    ) -> dict[str, Any]:
        encoded_body = parse.urlencode(payload).encode("utf-8")
        http_request = request.Request(
            url,
            data=encoded_body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                return _json_response(response.read())
        except error.HTTPError as exc:
            error_payload = _json_response(exc.read())
            if allow_oauth_error and isinstance(error_payload.get("error"), str):
                return error_payload
            raise OIDCAuthenticationError("OIDC endpoint rejected the request") from exc
        except (TimeoutError, error.URLError) as exc:
            raise OIDCAuthenticationError("OIDC endpoint request failed") from exc


def _verify_signature(
    alg: str,
    jwk: dict[str, Any],
    signing_input: bytes,
    signature: bytes,
) -> None:
    kty = jwk.get("kty")
    if alg.startswith("HS") and kty != "oct":
        raise OIDCAuthenticationError("OIDC ID token algorithm is incompatible with JWKS key")
    if alg == "HS256":
        secret = _b64url_decode(_required_string(jwk, "k"))
        expected = hmac.new(secret, signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, signature):
            raise OIDCAuthenticationError("OIDC ID token signature was invalid")
        return
    if alg == "RS256" and kty == "RSA":
        _verify_rs256(jwk, signing_input, signature)
        return
    raise OIDCAuthenticationError("OIDC ID token uses an unsupported algorithm")


def _verify_rs256(jwk: dict[str, Any], signing_input: bytes, signature: bytes) -> None:
    n = int.from_bytes(_b64url_decode(_required_string(jwk, "n")), "big")
    e = int.from_bytes(_b64url_decode(_required_string(jwk, "e")), "big")
    key_bytes = (n.bit_length() + 7) // 8
    if len(signature) != key_bytes:
        raise OIDCAuthenticationError("OIDC ID token signature was invalid")
    decoded = pow(int.from_bytes(signature, "big"), e, n).to_bytes(key_bytes, "big")
    digest = hashlib.sha256(signing_input).digest()
    expected_suffix = RSA_SHA256_DIGEST_INFO + digest
    padding_length = key_bytes - len(expected_suffix) - 3
    if padding_length < 8:
        raise OIDCAuthenticationError("OIDC JWKS RSA key is too small")
    expected = b"\x00\x01" + (b"\xff" * padding_length) + b"\x00" + expected_suffix
    if not hmac.compare_digest(decoded, expected):
        raise OIDCAuthenticationError("OIDC ID token signature was invalid")


def _decode_jwt(token: str) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    parts = token.split(".")
    if len(parts) != 3:
        raise OIDCAuthenticationError("OIDC ID token must have three JWT parts")
    header = _json_response(_b64url_decode(parts[0]))
    claims = _json_response(_b64url_decode(parts[1]))
    signature = _b64url_decode(parts[2])
    return header, claims, f"{parts[0]}.{parts[1]}".encode("ascii"), signature


def _json_response(value: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OIDCAuthenticationError("OIDC endpoint returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise OIDCAuthenticationError("OIDC endpoint JSON must be an object")
    return payload


def _string_endpoint(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise OIDCAuthenticationError(f"OIDC discovery metadata missing {key}")
    return value


def _required_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise OIDCAuthenticationError(f"OIDC token missing {key}")
    return value


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    return value if isinstance(value, str) and value else None


def _timestamp_claim(payload: dict[str, Any], key: str) -> datetime:
    value = payload.get(key)
    if not isinstance(value, int | float):
        raise OIDCAuthenticationError(f"OIDC token missing {key}")
    return datetime.fromtimestamp(value, tz=UTC)


def _optional_timestamp_claim(payload: dict[str, Any], key: str) -> datetime | None:
    if key not in payload:
        return None
    return _timestamp_claim(payload, key)


def _groups_from_claim(value: Any) -> list[str]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    if isinstance(value, str) and value:
        return [value]
    return []


def _token_identifier(claims: dict[str, Any]) -> str:
    jti = claims.get("jti")
    if isinstance(jti, str) and jti:
        return jti
    seed = f"{claims.get('iss', '')}:{claims.get('sub', '')}:{claims.get('iat', '')}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _pkce_verifier() -> str:
    return secrets.token_urlsafe(48)


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padded = value + ("=" * ((4 - len(value) % 4) % 4))
    try:
        return base64.urlsafe_b64decode(padded.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise OIDCAuthenticationError("OIDC token contained invalid base64url") from exc
