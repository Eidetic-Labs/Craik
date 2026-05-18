"""OIDC token-exchange secret manager."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from urllib import error, parse, request

from craik.runtime.auth.sources.secret_ref import SecretRefCredentialError
from craik.runtime.auth.url_safety import require_https_url
from craik.runtime.auth.workload import WorkloadIdentityError, WorkloadIdentityProvider

TOKEN_EXCHANGE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:token-exchange"
OIDC_SUBJECT_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:id_token"


@dataclass
class OIDCTokenExchangeSecretManager:
    """Exchange workload OIDC tokens for short-lived provider credentials."""

    workload_identity_provider: WorkloadIdentityProvider
    exchange_endpoint: str
    audience: str
    target_token_type: str
    timeout_seconds: float = 5.0
    safety_margin_seconds: int = 30
    allow_loopback_http: bool = False
    _cached_credential: str | None = field(default=None, init=False)
    _expires_at: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        require_https_url(
            self.exchange_endpoint,
            allow_loopback_http=self.allow_loopback_http,
            error_type=SecretRefCredentialError,
        )

    def resolve(self, ref: str) -> str:
        """Return an exchanged credential for a secret reference."""
        now = time.monotonic()
        if self._cached_credential and now < self._expires_at - self.safety_margin_seconds:
            return self._cached_credential
        try:
            workload_token = self.workload_identity_provider.get_token(self.audience)
        except WorkloadIdentityError as exc:
            raise SecretRefCredentialError("workload identity token is unavailable") from exc
        credential, expires_in = self._exchange(workload_token, ref)
        self._cached_credential = credential
        self._expires_at = now + expires_in
        return credential

    def _exchange(self, workload_token: str, ref: str) -> tuple[str, int]:
        payload = {
            "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
            "subject_token": workload_token,
            "subject_token_type": OIDC_SUBJECT_TOKEN_TYPE,
            "audience": self.audience,
            "requested_token_type": self.target_token_type,
            "resource": ref,
        }
        body = parse.urlencode(payload).encode("utf-8")
        http_request = request.Request(
            require_https_url(
                self.exchange_endpoint,
                allow_loopback_http=self.allow_loopback_http,
                error_type=SecretRefCredentialError,
            ),
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except (TimeoutError, error.URLError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise SecretRefCredentialError("OIDC token exchange failed") from exc
        if not isinstance(response_payload, dict):
            raise SecretRefCredentialError("OIDC token exchange response was invalid")
        credential = response_payload.get("access_token")
        if not isinstance(credential, str) or not credential:
            credential = response_payload.get("issued_token")
        if not isinstance(credential, str) or not credential:
            raise SecretRefCredentialError(
                "OIDC token exchange response did not include credential"
            )
        expires_in = response_payload.get("expires_in", 300)
        expires_in = expires_in if isinstance(expires_in, int | float) else 300
        return credential, max(1, int(expires_in))
