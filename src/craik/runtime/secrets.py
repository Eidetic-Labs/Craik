"""Reference-only secret resolution helpers."""

from __future__ import annotations

import os
from pathlib import Path

from craik.contracts.models import CraikModel


class SecretNotFoundError(RuntimeError):
    """Raised when a referenced secret cannot be resolved."""


class SecretRef(CraikModel):
    """Reference to a secret stored outside Craik state."""

    env_var: str
    dotenv_path: Path | None = None


class SecretResolver:
    """Resolve secrets from environment variables or a dotenv file."""

    def resolve(self, ref: SecretRef) -> str:
        """Resolve a secret value without exposing reference names in errors."""
        value = os.environ.get(ref.env_var)
        if value:
            return value
        if ref.dotenv_path is not None:
            value = _read_dotenv(ref.dotenv_path).get(ref.env_var)
            if value:
                return value
        raise SecretNotFoundError("secret reference could not be resolved")


def _read_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = _unquote(value.strip())
    return values


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
