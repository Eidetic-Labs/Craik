"""Cache-control parsing for operator authentication metadata."""

from __future__ import annotations

from collections.abc import Mapping


def cache_control_ttl_seconds(headers: Mapping[str, str], configured_ttl: int) -> int:
    """Return the effective cache TTL from response headers."""
    cache_control = headers.get("Cache-Control") or headers.get("cache-control") or ""
    directives = {
        part.strip().lower()
        for part in cache_control.split(",")
        if part.strip()
    }
    if "no-cache" in directives or "must-revalidate" in directives:
        return 0
    for directive in directives:
        if not directive.startswith("max-age="):
            continue
        try:
            max_age = int(directive.removeprefix("max-age="))
        except ValueError:
            return configured_ttl
        return max(0, min(max_age, configured_ttl))
    return configured_ttl
