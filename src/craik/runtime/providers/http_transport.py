"""urllib-backed provider HTTP transport."""

from __future__ import annotations

import json
import threading
from collections.abc import Callable, Iterator
from typing import Any
from urllib import error, request

from craik.runtime.policy.redaction import redact
from craik.runtime.providers.provider_transport import ProviderFamily, ProviderTransportError

_SAFE_ERROR_HEADER_NAMES = frozenset(
    {
        "content-type",
        "date",
        "retry-after",
        "x-request-id",
    }
)


class HTTPTransport:
    """POST provider payloads over HTTP and yield parsed response chunks."""

    def __init__(
        self,
        *,
        family: ProviderFamily,
        base_url: str,
        headers_factory: Callable[[], dict[str, str]],
        timeout_seconds: float,
        cancel_event: threading.Event | None = None,
    ) -> None:
        self._family = family
        self._base_url = base_url.rstrip("/")
        self._headers_factory = headers_factory
        self._timeout_seconds = timeout_seconds
        self._cancel_event = cancel_event

    @property
    def family(self) -> ProviderFamily:
        """Provider API family this transport speaks."""
        return self._family

    @property
    def cancel_event(self) -> threading.Event | None:
        """Optional cancellation event checked before requests and between chunks."""
        return self._cancel_event

    def send(self, payload: dict[str, Any], *, stream: bool) -> Iterator[dict[str, Any]]:
        """Send a JSON payload and yield parsed JSON or SSE response chunks."""
        _raise_if_cancelled(self._cancel_event)
        path = str(payload.get("_path", ""))
        body_payload = {key: value for key, value in payload.items() if not key.startswith("_")}
        body = json.dumps(body_payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream" if stream else "application/json",
            **self._headers_factory(),
        }
        http_request = request.Request(
            _join_url(self._base_url, path),
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self._timeout_seconds) as response:
                if stream:
                    yield from _iter_sse(response, cancel_event=self._cancel_event)
                    return
                parsed = json.loads(response.read().decode("utf-8"))
                if isinstance(parsed, dict):
                    yield parsed
                    return
                raise ProviderTransportError("provider response JSON was not an object")
        except error.HTTPError as exc:
            raise _transport_http_error(exc) from exc
        except TimeoutError as exc:
            raise _transport_network_error("provider transport timed out") from exc
        except error.URLError as exc:
            raise _transport_network_error("provider transport URL request failed") from exc


def _iter_sse(
    response: Any,
    *,
    cancel_event: threading.Event | None = None,
) -> Iterator[dict[str, Any]]:
    while True:
        _raise_if_cancelled(cancel_event)
        raw_line = response.readline()
        if not raw_line:
            return
        line = raw_line.decode("utf-8").strip()
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if data == "[DONE]":
            return
        parsed = json.loads(data)
        if isinstance(parsed, dict):
            yield parsed
            continue
        raise ProviderTransportError("provider stream JSON event was not an object")


def _transport_http_error(exc: error.HTTPError) -> ProviderTransportError:
    body = exc.read().decode("utf-8", errors="replace")
    redacted_body = str(redact(body).value)
    safe_headers = _safe_error_headers({str(key): str(value) for key, value in exc.headers.items()})
    retry_after_seconds = _retry_after(safe_headers)
    return ProviderTransportError(
        f"provider transport HTTP {exc.code}: {redacted_body}",
        status_code=exc.code,
        body=redacted_body,
        headers=safe_headers,
        retry_after_seconds=retry_after_seconds,
        retryable=exc.code in {408, 409, 429, 500, 502, 503, 504, 529},
    )


def _transport_network_error(message: str) -> ProviderTransportError:
    return ProviderTransportError(message, retryable=True)


def _raise_if_cancelled(cancel_event: threading.Event | None) -> None:
    if cancel_event is not None and cancel_event.is_set():
        raise ProviderTransportError("provider transport cancelled", retryable=False)


def _retry_after(headers: dict[str, str]) -> int | None:
    for key, value in headers.items():
        if key.lower() == "retry-after" and value.isdigit():
            return int(value)
    return None


def _safe_error_headers(headers: dict[str, str]) -> dict[str, str]:
    safe_headers: dict[str, str] = {}
    for raw_key, raw_value in headers.items():
        key = raw_key.lower()
        if key not in _SAFE_ERROR_HEADER_NAMES:
            continue
        safe_headers[key] = str(redact(raw_value).value)
    return safe_headers


def _join_url(base_url: str, path: str) -> str:
    if not path:
        return base_url
    normalized_path = path.lstrip("/")
    if base_url.endswith("/v1") and normalized_path.startswith("v1/"):
        normalized_path = normalized_path.removeprefix("v1/")
    return f"{base_url}/{normalized_path}"
