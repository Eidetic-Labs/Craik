"""URL validation helpers for authentication network calls."""

from __future__ import annotations

from urllib.parse import urlparse

_LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}


def require_https_url(
    url: str,
    *,
    allow_loopback_http: bool = False,
    error_type: type[Exception] = ValueError,
) -> str:
    """Return url only when it is HTTPS or explicitly allowed loopback HTTP."""
    parsed = urlparse(url)
    if parsed.scheme == "https":
        return url
    host = (parsed.hostname or "").lower()
    if allow_loopback_http and parsed.scheme == "http" and host in _LOOPBACK_HOSTS:
        return url
    raise error_type("endpoint must use HTTPS (loopback HTTP requires explicit opt-in)")
