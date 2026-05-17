"""Secret-reference credential source.

Secret managers implement the small ``SecretManager`` protocol so deployments
can plug in Vault, AWS Secrets Manager, cloud KMS brokers, or internal secret
services without changing Craik's provider runtime. Built-in managers cover
environment variables and local files for development and tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from craik.runtime.auth.profile import CredentialStatus
from craik.runtime.providers.provider_transport import ProviderFamily
from craik.runtime.secrets import SecretNotFoundError, SecretRef, SecretResolver


class SecretRefCredentialError(RuntimeError):
    """Raised when a secret-reference credential cannot resolve."""


class SecretManager(Protocol):
    """Resolve an opaque secret reference into credential material."""

    def resolve(self, ref: str) -> str:
        """Return credential material for a reference."""
        ...


@dataclass(frozen=True)
class EnvVarSecretManager:
    """Secret manager that treats refs as environment variable names."""

    resolver: SecretResolver = SecretResolver()

    def resolve(self, ref: str) -> str:
        """Resolve a secret from an environment variable."""
        try:
            return self.resolver.resolve(SecretRef(env_var=ref))
        except SecretNotFoundError as exc:
            raise SecretRefCredentialError("secret reference could not be resolved") from exc


@dataclass(frozen=True)
class FileSecretManager:
    """Secret manager that reads credential material from a local file path."""

    def resolve(self, ref: str) -> str:
        """Resolve a secret from a file path."""
        try:
            value = Path(ref).expanduser().read_text(encoding="utf-8").strip()
        except FileNotFoundError as exc:
            raise SecretRefCredentialError("secret reference could not be resolved") from exc
        if not value:
            raise SecretRefCredentialError("secret reference could not be resolved")
        return value


@dataclass(frozen=True)
class SecretRefCredentialSource:
    """Resolve provider credentials through a pluggable secret manager."""

    ref: str
    manager: SecretManager

    def headers_for(self, family: ProviderFamily) -> dict[str, str]:
        """Return provider-specific headers from a resolved secret reference."""
        secret = self._resolve_secret()
        if family == "anthropic":
            return {
                "anthropic-version": "2023-06-01",
                "x-api-key": secret,
            }
        return {"Authorization": f"Bearer {secret}"}

    def status(self) -> CredentialStatus:
        """Check whether the secret reference resolves without exposing it."""
        try:
            self._resolve_secret()
        except SecretRefCredentialError as exc:
            return CredentialStatus(status="rejected", detail=str(exc))
        return CredentialStatus(status="ok")

    def _resolve_secret(self) -> str:
        secret = self.manager.resolve(self.ref)
        if not secret:
            raise SecretRefCredentialError("secret reference could not be resolved")
        return secret
