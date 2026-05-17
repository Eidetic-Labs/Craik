from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from craik.runtime.http_transport import HTTPTransport
from craik.runtime.provider_transport import ProviderTransportError


def test_http_transport_yields_non_streaming_json_response() -> None:
    seen: dict[str, Any] = {}

    def handle(payload: dict[str, Any], headers: dict[str, str]) -> _StubResponse:
        seen["payload"] = payload
        seen["authorization"] = headers.get("Authorization")
        return _json_response({"id": "resp_1", "output_text": "ok"})

    with _stub_server(handle) as server:
        transport = HTTPTransport(
            family="openai",
            base_url=server.url,
            headers={"Authorization": "Bearer test-token"},
            timeout_seconds=5,
        )

        chunks = list(transport.send({"_path": "/v1/responses", "model": "gpt-test"}, stream=False))

    assert chunks == [{"id": "resp_1", "output_text": "ok"}]
    assert seen["payload"] == {"model": "gpt-test"}
    assert seen["authorization"] == "Bearer test-token"


def test_http_transport_yields_sse_json_chunks() -> None:
    def handle(payload: dict[str, Any], headers: dict[str, str]) -> _StubResponse:
        return _sse_response(
            [
                'event: message\n',
                'data: {"delta":"Hel"}\n\n',
                ': keep-alive\n',
                'data: {"delta":"lo"}\n\n',
                'data: [DONE]\n\n',
            ]
        )

    with _stub_server(handle) as server:
        transport = HTTPTransport(
            family="anthropic",
            base_url=server.url,
            headers={},
            timeout_seconds=5,
        )

        chunks = list(transport.send({"_path": "/v1/messages", "stream": True}, stream=True))

    assert chunks == [{"delta": "Hel"}, {"delta": "lo"}]


def test_http_transport_error_redacts_body_and_preserves_retry_after() -> None:
    def handle(payload: dict[str, Any], headers: dict[str, str]) -> _StubResponse:
        return _json_response(
            {"error": "token sk-test-secret failed"},
            status=429,
            headers={"Retry-After": "3"},
        )

    with _stub_server(handle) as server:
        transport = HTTPTransport(
            family="openai",
            base_url=server.url,
            headers={"Authorization": "Bearer secret-auth-token"},
            timeout_seconds=5,
        )

        try:
            list(transport.send({"_path": "/v1/responses"}, stream=False))
        except ProviderTransportError as exc:
            error = exc
        else:  # pragma: no cover - defensive assertion path
            raise AssertionError("expected ProviderTransportError")

    assert error.status_code == 429
    assert error.retry_after_seconds == 3
    assert "sk-test-secret" not in str(error)
    assert "secret-auth-token" not in str(error)
    assert error.body is not None
    assert "sk-test-secret" not in error.body


class _StubResponse:
    def __init__(
        self,
        *,
        body: bytes,
        status: int = 200,
        headers: dict[str, str] | None = None,
        content_type: str = "application/json",
    ) -> None:
        self.body = body
        self.status = status
        self.headers = {"Content-Type": content_type, **(headers or {})}


def _json_response(
    payload: dict[str, Any],
    *,
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> _StubResponse:
    return _StubResponse(body=json.dumps(payload).encode("utf-8"), status=status, headers=headers)


def _sse_response(lines: list[str]) -> _StubResponse:
    return _StubResponse(
        body="".join(lines).encode("utf-8"),
        content_type="text/event-stream",
    )


class _Node:
    def __init__(self, server: HTTPServer, thread: threading.Thread) -> None:
        self._server = server
        self._thread = thread
        self.url = f"http://127.0.0.1:{server.server_port}"

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)

    def __enter__(self) -> _Node:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def _stub_server(handler: Any) -> _Node:
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length).decode("utf-8") or "{}")
            response = handler(payload, dict(self.headers.items()))
            self.send_response(response.status)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(response.body)))
            self.end_headers()
            self.wfile.write(response.body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return _Node(server, thread)
