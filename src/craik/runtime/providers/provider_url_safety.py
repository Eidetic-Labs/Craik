"""Provider URL validation helpers."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse


class ProviderURLSafetyError(ValueError):
    """Raised when a provider URL is unsafe for credential-bearing calls."""


def assert_safe_provider_url(url: str, *, allow_local: bool) -> None:
    """Validate a provider URL before credential-bearing HTTP requests."""
    parsed = urlparse(url)
    allowed_schemes = {"https"} | ({"http"} if allow_local else set())
    if parsed.scheme not in allowed_schemes:
        raise ProviderURLSafetyError("provider base_url must use HTTPS")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ProviderURLSafetyError("provider base_url is missing a host")
    if host in {"localhost", "127.0.0.1", "::1"}:
        if allow_local:
            return
        raise ProviderURLSafetyError("provider base_url points to a private network")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return
    if ip.is_loopback and allow_local:
        return
    if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved:
        raise ProviderURLSafetyError("provider base_url points to a private network")
