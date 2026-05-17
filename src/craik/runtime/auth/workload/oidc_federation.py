"""Workload-identity OIDC token providers."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
from urllib import error, parse, request

DEFAULT_KUBERNETES_TOKEN_PATH = Path("/var/run/secrets/tokens/craik")


class WorkloadIdentityError(RuntimeError):
    """Raised when a workload identity token cannot be resolved."""


class WorkloadIdentityProvider(Protocol):
    """Return a current host-issued OIDC token for an audience."""

    def get_token(self, audience: str) -> str:
        """Return a current workload OIDC token for the requested audience."""
        ...


@dataclass
class GitHubActionsWorkloadIdentity:
    """Resolve OIDC tokens from the GitHub Actions runtime environment."""

    env: dict[str, str] | None = None
    timeout_seconds: float = 5.0

    def get_token(self, audience: str) -> str:
        """Request a GitHub Actions OIDC token for an audience."""
        values = os.environ if self.env is None else self.env
        base_url = values.get("ACTIONS_ID_TOKEN_REQUEST_URL")
        request_token = values.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
        if not base_url or not request_token:
            raise WorkloadIdentityError("GitHub Actions OIDC environment is not available")
        url = _url_with_audience(base_url, audience)
        http_request = request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {request_token}",
            },
            method="GET",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (TimeoutError, error.URLError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise WorkloadIdentityError("GitHub Actions OIDC token request failed") from exc
        if not isinstance(payload, dict):
            raise WorkloadIdentityError("GitHub Actions OIDC response was invalid")
        token = payload.get("value")
        if not isinstance(token, str) or not token:
            raise WorkloadIdentityError("GitHub Actions OIDC response did not include a token")
        return token


@dataclass
class GenericFileTokenIdentity:
    """Resolve workload OIDC tokens from a local file."""

    path: Path
    ttl_seconds: int = 300
    refresh_margin_seconds: int = 30
    _cached_token: str | None = field(default=None, init=False)
    _expires_at: float = field(default=0.0, init=False)

    def get_token(self, audience: str) -> str:
        """Return the current file-backed token, re-reading before expiry."""
        del audience
        now = time.monotonic()
        if self._cached_token and now < self._expires_at - self.refresh_margin_seconds:
            return self._cached_token
        token = _read_token_file(self.path, "workload token file")
        self._cached_token = token
        self._expires_at = now + self.ttl_seconds
        return token


@dataclass
class KubernetesProjectedTokenIdentity(GenericFileTokenIdentity):
    """Resolve a Kubernetes projected service-account OIDC token."""

    path: Path = DEFAULT_KUBERNETES_TOKEN_PATH


@dataclass
class EnvVarTokenIdentity:
    """Resolve workload OIDC tokens from an environment variable."""

    env_var: str
    env: dict[str, str] | None = None
    ttl_seconds: int = 300
    refresh_margin_seconds: int = 30
    _cached_token: str | None = field(default=None, init=False)
    _expires_at: float = field(default=0.0, init=False)

    def get_token(self, audience: str) -> str:
        """Return the current env-backed token, re-reading before expiry."""
        del audience
        now = time.monotonic()
        if self._cached_token and now < self._expires_at - self.refresh_margin_seconds:
            return self._cached_token
        values = os.environ if self.env is None else self.env
        token = values.get(self.env_var)
        if not token:
            raise WorkloadIdentityError("workload token environment variable is not available")
        self._cached_token = token
        self._expires_at = now + self.ttl_seconds
        return token


def _read_token_file(path: Path, label: str) -> str:
    try:
        token = path.expanduser().read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise WorkloadIdentityError(f"{label} is not available") from exc
    except OSError as exc:
        raise WorkloadIdentityError(f"{label} could not be read") from exc
    if not token:
        raise WorkloadIdentityError(f"{label} is empty")
    return token


def _url_with_audience(base_url: str, audience: str) -> str:
    parsed = parse.urlparse(base_url)
    query = parse.parse_qs(parsed.query)
    query["audience"] = [audience]
    return parse.urlunparse(parsed._replace(query=parse.urlencode(query, doseq=True)))
