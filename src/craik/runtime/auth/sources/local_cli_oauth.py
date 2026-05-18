"""Local CLI OAuth credential source.

This source reads credentials maintained by a vendor CLI, refreshes near-expiry
tokens when a refresh endpoint is configured, and returns provider headers
without logging or surfacing token material. Subscription OAuth credentials may
route through a provider billing pool that differs from API-key calls; callers
should carry the profile id into receipts so operators can distinguish them.
"""

from __future__ import annotations

import json
import os
import stat
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import error, request

from craik.runtime.auth.profile import CredentialStatus
from craik.runtime.providers.provider_transport import ProviderFamily

DEFAULT_CLAUDE_CREDENTIALS_PATH = Path("~/.claude/.credentials.json")
OWNER_ONLY_FILE_MODE = 0o600


class LocalCLICredentialError(RuntimeError):
    """Raised when local CLI OAuth credentials cannot be resolved."""


@dataclass(frozen=True)
class LocalCLICredentialSource:
    """Read and refresh OAuth credentials written by a local vendor CLI."""

    credentials_path: Path = DEFAULT_CLAUDE_CREDENTIALS_PATH
    refresh_endpoint: str | None = None
    client_id: str | None = None
    refresh_margin_seconds: int = 300
    timeout_seconds: float = 5.0
    oauth_client_headers: dict[str, str] = field(default_factory=dict)

    def headers_for(self, family: ProviderFamily) -> dict[str, str]:
        """Return provider-specific headers for a local CLI OAuth token."""
        access_token = self._current_access_token()
        if family == "anthropic":
            return {
                "Authorization": f"Bearer {access_token}",
                "anthropic-version": "2023-06-01",
                **self.oauth_client_headers,
            }
        return {"Authorization": f"Bearer {access_token}", **self.oauth_client_headers}

    def status(self) -> CredentialStatus:
        """Check whether the local CLI credential file is readable and current."""
        try:
            payload = self._read_credentials()
            token = _extract_token_payload(payload)
            expires_at = _expires_at(token)
        except LocalCLICredentialError as exc:
            return CredentialStatus(status="rejected", detail=str(exc))
        if expires_at is not None and self._needs_refresh(expires_at):
            return CredentialStatus(
                status="expired",
                detail="local CLI OAuth token requires refresh",
                expires_at=expires_at,
            )
        return CredentialStatus(status="ok", expires_at=expires_at)

    def _current_access_token(self) -> str:
        payload = self._read_credentials()
        token = _extract_token_payload(payload)
        expires_at = _expires_at(token)
        if expires_at is not None and self._needs_refresh(expires_at):
            token = self._refresh_token(payload, token)
        access_token = _string_value(token, "access_token", "accessToken")
        if not access_token:
            raise LocalCLICredentialError("local CLI credentials missing access token")
        return access_token

    def _read_credentials(self) -> dict[str, Any]:
        path = _validated_credentials_path(self.credentials_path, must_exist=True)
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise LocalCLICredentialError("local CLI credentials file not found") from exc
        except json.JSONDecodeError as exc:
            raise LocalCLICredentialError("local CLI credentials file is invalid JSON") from exc
        if not isinstance(parsed, dict):
            raise LocalCLICredentialError("local CLI credentials file must contain an object")
        return parsed

    def _refresh_token(
        self,
        payload: dict[str, Any],
        token: dict[str, Any],
    ) -> dict[str, Any]:
        refresh_token = _string_value(token, "refresh_token", "refreshToken")
        if not refresh_token:
            raise LocalCLICredentialError("local CLI credentials missing refresh token")
        if self.refresh_endpoint is None:
            raise LocalCLICredentialError("local CLI OAuth refresh endpoint is not configured")
        body: dict[str, Any] = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        if self.client_id:
            body["client_id"] = self.client_id
        http_request = request.Request(
            self.refresh_endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", **self.oauth_client_headers},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                refreshed = json.loads(response.read().decode("utf-8"))
        except TimeoutError as exc:
            raise LocalCLICredentialError("local CLI OAuth refresh timed out") from exc
        except error.URLError as exc:
            raise LocalCLICredentialError("local CLI OAuth refresh failed") from exc
        if not isinstance(refreshed, dict):
            raise LocalCLICredentialError("local CLI OAuth refresh response was invalid")
        updated = _merge_refreshed_token(token, refreshed)
        _write_token_payload(payload, updated)
        self._write_credentials(payload)
        return updated

    def _write_credentials(self, payload: dict[str, Any]) -> None:
        path = _validated_credentials_path(self.credentials_path, must_exist=False)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            text=True,
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, sort_keys=True)
                handle.write("\n")
            if os.name == "posix":
                temp_path.chmod(OWNER_ONLY_FILE_MODE)
            os.replace(temp_path, path)
            if os.name == "posix":
                path.chmod(OWNER_ONLY_FILE_MODE)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _needs_refresh(self, expires_at: datetime) -> bool:
        margin = timedelta(seconds=self.refresh_margin_seconds)
        return expires_at <= datetime.now(UTC) + margin


def _validated_credentials_path(path: Path, *, must_exist: bool) -> Path:
    expanded = path.expanduser()
    try:
        metadata = expanded.lstat()
    except FileNotFoundError as exc:
        if must_exist:
            raise LocalCLICredentialError("local CLI credentials file not found") from exc
        return expanded
    except OSError as exc:
        raise LocalCLICredentialError("local CLI credentials file could not be inspected") from exc
    if stat.S_ISLNK(metadata.st_mode):
        raise LocalCLICredentialError("local CLI credentials path must not be a symlink")
    if not stat.S_ISREG(metadata.st_mode):
        raise LocalCLICredentialError("local CLI credentials path must be a regular file")
    if os.name == "posix" and metadata.st_mode & 0o077:
        raise LocalCLICredentialError("local CLI credentials file must be owner-only (0600)")
    return expanded


def _extract_token_payload(payload: dict[str, Any]) -> dict[str, Any]:
    nested = payload.get("claudeAiOauth")
    if isinstance(nested, dict):
        return nested
    nested = payload.get("oauth")
    if isinstance(nested, dict):
        return nested
    return payload


def _write_token_payload(payload: dict[str, Any], token: dict[str, Any]) -> None:
    if isinstance(payload.get("claudeAiOauth"), dict):
        payload["claudeAiOauth"] = token
        return
    if isinstance(payload.get("oauth"), dict):
        payload["oauth"] = token
        return
    payload.update(token)


def _merge_refreshed_token(current: dict[str, Any], refreshed: dict[str, Any]) -> dict[str, Any]:
    access_token = _string_value(refreshed, "access_token", "accessToken")
    if not access_token:
        raise LocalCLICredentialError("local CLI OAuth refresh response missing access token")
    updated = dict(current)
    updated["access_token"] = access_token
    refresh_token = _string_value(refreshed, "refresh_token", "refreshToken")
    if refresh_token:
        updated["refresh_token"] = refresh_token
    expires_at = _refreshed_expires_at(refreshed)
    if expires_at is not None:
        updated["expires_at"] = expires_at.isoformat()
    return updated


def _expires_at(token: dict[str, Any]) -> datetime | None:
    value = token.get("expires_at", token.get("expiresAt"))
    if value is None:
        return None
    if isinstance(value, int | float):
        return datetime.fromtimestamp(value, tz=UTC)
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise LocalCLICredentialError("local CLI credential expiry is invalid") from exc
        return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
    raise LocalCLICredentialError("local CLI credential expiry is invalid")


def _refreshed_expires_at(payload: dict[str, Any]) -> datetime | None:
    expires_at = _expires_at(payload)
    if expires_at is not None:
        return expires_at
    expires_in = payload.get("expires_in", payload.get("expiresIn"))
    if isinstance(expires_in, int | float):
        return datetime.now(UTC) + timedelta(seconds=float(expires_in))
    return None


def _string_value(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return ""
