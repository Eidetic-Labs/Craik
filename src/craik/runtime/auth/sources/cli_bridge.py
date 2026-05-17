"""Credential source backed by a configured vendor CLI command."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from craik.runtime.auth.profile import CredentialStatus
from craik.runtime.providers.provider_transport import ProviderFamily

TokenExtractor = Literal["stdout_json", "stdout_line", "credentials_file"]


class CLIBridgeCredentialError(RuntimeError):
    """Raised when a CLI bridge cannot resolve credential material."""


@dataclass(frozen=True)
class CLIBridgeCredentialSource:
    """Resolve credentials by delegating to a configured local command."""

    command: tuple[str, ...]
    token_extractor: TokenExtractor
    key_path: tuple[str, ...] = ("token",)
    credentials_file_path: Path | None = None
    timeout_seconds: float = 5.0

    def headers_for(self, family: ProviderFamily) -> dict[str, str]:
        """Return provider-specific headers for a bridged credential."""
        token = self._resolve_token()
        if family == "anthropic":
            return {
                "Authorization": f"Bearer {token}",
                "anthropic-version": "2023-06-01",
            }
        return {"Authorization": f"Bearer {token}"}

    def status(self) -> CredentialStatus:
        """Check whether the bridge can resolve a token without exposing it."""
        try:
            self._resolve_token()
        except CLIBridgeCredentialError as exc:
            return CredentialStatus(status="rejected", detail=str(exc))
        return CredentialStatus(status="ok")

    def _resolve_token(self) -> str:
        if self.token_extractor == "credentials_file":
            if self.credentials_file_path is None:
                raise CLIBridgeCredentialError("CLI bridge credentials file is not configured")
            parsed = _json_file(self.credentials_file_path)
            return _token_from_json(parsed, self.key_path)

        stdout = self._command_stdout()
        if self.token_extractor == "stdout_line":
            token = next((line.strip() for line in stdout.splitlines() if line.strip()), "")
            if not token:
                raise CLIBridgeCredentialError("CLI bridge command produced no token")
            return token
        if self.token_extractor == "stdout_json":
            try:
                parsed = json.loads(stdout)
            except json.JSONDecodeError as exc:
                raise CLIBridgeCredentialError("CLI bridge command output was not JSON") from exc
            if not isinstance(parsed, dict):
                raise CLIBridgeCredentialError("CLI bridge command JSON was not an object")
            return _token_from_json(parsed, self.key_path)
        raise CLIBridgeCredentialError("unsupported CLI bridge token extractor")

    def _command_stdout(self) -> str:
        if not self.command:
            raise CLIBridgeCredentialError("CLI bridge command is empty")
        try:
            result = subprocess.run(
                list(self.command),
                capture_output=True,
                check=False,
                text=True,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise CLIBridgeCredentialError("CLI bridge command timed out") from exc
        except OSError as exc:
            raise CLIBridgeCredentialError("CLI bridge command could not be executed") from exc
        if result.returncode != 0:
            raise CLIBridgeCredentialError("CLI bridge command failed")
        return result.stdout


def _json_file(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.expanduser().read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CLIBridgeCredentialError("CLI bridge credentials file not found") from exc
    except json.JSONDecodeError as exc:
        raise CLIBridgeCredentialError("CLI bridge credentials file was not JSON") from exc
    if not isinstance(parsed, dict):
        raise CLIBridgeCredentialError("CLI bridge credentials file JSON was not an object")
    return parsed


def _token_from_json(payload: dict[str, Any], key_path: tuple[str, ...]) -> str:
    current: Any = payload
    for key in key_path:
        if not isinstance(current, dict):
            raise CLIBridgeCredentialError("CLI bridge token path did not resolve")
        current = current.get(key)
    if not isinstance(current, str) or not current:
        raise CLIBridgeCredentialError("CLI bridge token path did not resolve")
    return current
