"""Owner-only operator session persistence."""

from __future__ import annotations

import json
import os
import stat
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError

from craik.runtime.auth.operator.oidc import OIDCAuthenticator
from craik.runtime.auth.operator.session import OperatorSession
from craik.runtime.paths import ensure_craik_home, resolve_craik_home

OPERATOR_SESSION_FILENAME = "operator-session.json"
OPERATOR_SESSION_SCHEMA_VERSION = 1
OWNER_ONLY_FILE_MODE = 0o600


class OperatorSessionStoreError(RuntimeError):
    """Raised when operator session state cannot be loaded or written."""


class OperatorSessionNotFoundError(OperatorSessionStoreError):
    """Raised when no operator session is available."""


class OperatorSessionStore:
    """Read and write the active operator session in a Craik home directory."""

    def __init__(self, home: Path) -> None:
        self.home = home.expanduser().resolve()
        self.path = self.home / OPERATOR_SESSION_FILENAME
        self.lock_path = self.home / f"{OPERATOR_SESSION_FILENAME}.lock"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> OperatorSessionStore:
        """Create a store from CRAIK_HOME, ensuring the home layout exists."""
        ensure_craik_home(env)
        return cls(resolve_craik_home(env))

    def get(
        self,
        *,
        authenticator: OIDCAuthenticator | None = None,
        refresh_margin_seconds: int = 300,
    ) -> OperatorSession:
        """Return the active session, refreshing near-expiry when possible."""
        with self._locked():
            record = self._read_unlocked()
            if record is None:
                raise OperatorSessionNotFoundError("operator session not found")
            session = cast(OperatorSession, record["session"])
            refresh_token = record.get("refresh_token")
            if (
                authenticator is not None
                and isinstance(refresh_token, str)
                and _needs_refresh(session, refresh_margin_seconds)
            ):
                session, refresh_token = authenticator.refresh_session(refresh_token)
                self._write_unlocked(session, refresh_token)
            return session

    def put(self, session: OperatorSession, *, refresh_token: str | None = None) -> None:
        """Persist the active operator session."""
        with self._locked():
            self._write_unlocked(session, refresh_token)

    def delete(
        self,
        *,
        authenticator: OIDCAuthenticator | None = None,
        revoke: bool = True,
    ) -> bool:
        """Delete the active session and best-effort revoke its refresh token."""
        with self._locked():
            record = self._read_unlocked()
            refresh_token = record.get("refresh_token") if record is not None else None
            revoked = False
            if revoke and authenticator is not None and isinstance(refresh_token, str):
                revoked = authenticator.revoke_refresh_token(refresh_token)
            self.path.unlink(missing_ok=True)
            return revoked

    def _read_unlocked(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise OperatorSessionStoreError("operator session store contains invalid JSON") from exc
        if (
            not isinstance(payload, dict)
            or payload.get("version") != OPERATOR_SESSION_SCHEMA_VERSION
        ):
            raise OperatorSessionStoreError("operator session store has unsupported schema version")
        try:
            session = OperatorSession.model_validate(payload.get("session"))
        except ValidationError as exc:
            raise OperatorSessionStoreError("operator session store contains invalid data") from exc
        refresh_token = payload.get("refresh_token")
        if refresh_token is not None and not isinstance(refresh_token, str):
            raise OperatorSessionStoreError("operator session refresh token must be a string")
        return {"session": session, "refresh_token": refresh_token}

    def _write_unlocked(
        self,
        session: OperatorSession,
        refresh_token: str | None,
    ) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": OPERATOR_SESSION_SCHEMA_VERSION,
            "session": session.model_dump(mode="json"),
            "refresh_token": refresh_token,
        }
        fd, temp_name = tempfile.mkstemp(
            prefix=".operator-session.",
            suffix=".tmp",
            dir=self.home,
            text=True,
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, sort_keys=True)
                handle.write("\n")
            if os.name == "posix":
                temp_path.chmod(OWNER_ONLY_FILE_MODE)
            os.replace(temp_path, self.path)
            if os.name == "posix":
                self.path.chmod(OWNER_ONLY_FILE_MODE)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    @contextmanager
    def _locked(self) -> Iterator[None]:
        self.home.mkdir(parents=True, exist_ok=True)
        if os.name == "posix":
            import fcntl

            with self.lock_path.open("a+", encoding="utf-8") as lock_file:
                fcntl.flock(lock_file, fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock_file, fcntl.LOCK_UN)
            return

        lock_fd: int | None = None
        while lock_fd is None:
            try:
                lock_fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            except FileExistsError:
                time.sleep(0.01)
        try:
            yield
        finally:
            os.close(lock_fd)
            self.lock_path.unlink(missing_ok=True)


def operator_session_store_owner_only(path: Path) -> bool:
    """Return whether an operator session file is owner-readable/writable only."""
    if os.name != "posix":
        return True
    mode = stat.S_IMODE(path.stat().st_mode)
    return mode == OWNER_ONLY_FILE_MODE


def _needs_refresh(session: OperatorSession, margin_seconds: int) -> bool:
    margin = timedelta(seconds=margin_seconds)
    return session.expires_at <= datetime.now(UTC) + margin
