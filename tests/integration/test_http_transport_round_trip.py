from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from craik.runtime.providers.http_transport import HTTPTransport
from craik.runtime.providers.provider_runtime import (
    OPENAI_OFFICIAL_DOCS,
    ChatCompletionsProviderAdapter,
    ProviderMessage,
    ProviderRuntimeConfig,
    ProviderRuntimeRequest,
)


@pytest.mark.integration
def test_http_transport_chat_completions_round_trip() -> None:
    request_bodies: list[dict[str, Any]] = []
    server = _start_server(_non_streaming_handler(request_bodies))
    try:
        adapter = _adapter_for_server(server)

        result = adapter.execute(
            ProviderRuntimeRequest(
                messages=[ProviderMessage(role="user", content="hi")],
                max_output_tokens=16,
            )
        )
    finally:
        _stop_server(server)

    assert request_bodies
    assert request_bodies[0]["model"] == "stub-model"
    assert request_bodies[0]["messages"] == [{"role": "user", "content": "hi"}]
    assert result.text == "stub HTTPTransport response"
    assert result.usage["total_tokens"] == 9
    assert result.model == "stub-model"


@pytest.mark.integration
def test_http_transport_chat_completions_sse_round_trip() -> None:
    request_bodies: list[dict[str, Any]] = []
    server = _start_server(_streaming_handler(request_bodies))
    try:
        adapter = _adapter_for_server(server)

        result = adapter.execute(
            ProviderRuntimeRequest(
                messages=[ProviderMessage(role="user", content="hi")],
                max_output_tokens=16,
                stream=True,
            )
        )
    finally:
        _stop_server(server)

    assert request_bodies
    assert request_bodies[0]["stream"] is True
    assert result.text == "stub HTTPTransport streaming response"
    assert result.usage["total_tokens"] == 9
    assert result.model == "stub-model"


def _adapter_for_server(server: HTTPServer) -> ChatCompletionsProviderAdapter:
    host, port = server.server_address
    base_url = f"http://{host}:{port}"
    return ChatCompletionsProviderAdapter(
        ProviderRuntimeConfig(
            provider_id="provider_http_transport_stub",
            provider_family="chat_completions",
            model="stub-model",
            secret_ref_name="",
            docs_refs=list(OPENAI_OFFICIAL_DOCS),
        ),
        transport=HTTPTransport(
            family="chat_completions",
            base_url=base_url,
            headers_factory=dict,
            timeout_seconds=5,
        ),
    )


def _start_server(handler: type[BaseHTTPRequestHandler]) -> HTTPServer:
    server = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _stop_server(server: HTTPServer) -> None:
    server.shutdown()
    server.server_close()


def _non_streaming_handler(
    request_bodies: list[dict[str, Any]],
) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            payload = _read_json_body(self)
            request_bodies.append(payload)
            if self.path != "/v1/chat/completions" or not _valid_chat_payload(payload):
                self.send_response(400)
                self.end_headers()
                return

            _write_json(
                self,
                {
                    "id": "chatcmpl-stub-1",
                    "model": "stub-model",
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "stub HTTPTransport response",
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 5,
                        "completion_tokens": 4,
                        "total_tokens": 9,
                    },
                },
            )

        def log_message(self, format: str, *args: object) -> None:
            return

    return Handler


def _streaming_handler(
    request_bodies: list[dict[str, Any]],
) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            payload = _read_json_body(self)
            request_bodies.append(payload)
            if self.path != "/v1/chat/completions" or not _valid_chat_payload(payload):
                self.send_response(400)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for chunk in _stream_chunks():
                self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
                self.wfile.flush()
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()

        def log_message(self, format: str, *args: object) -> None:
            return

    return Handler


def _stream_chunks() -> list[dict[str, Any]]:
    return [
        {
            "id": "chatcmpl-stub-stream",
            "model": "stub-model",
            "choices": [{"delta": {"content": "stub "}, "finish_reason": None}],
        },
        {
            "id": "chatcmpl-stub-stream",
            "model": "stub-model",
            "choices": [{"delta": {"content": "HTTPTransport "}, "finish_reason": None}],
        },
        {
            "id": "chatcmpl-stub-stream",
            "model": "stub-model",
            "choices": [
                {"delta": {"content": "streaming response"}, "finish_reason": "stop"}
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 4, "total_tokens": 9},
        },
    ]


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0"))
    body = handler.rfile.read(length)
    payload = json.loads(body.decode("utf-8"))
    assert isinstance(payload, dict)
    return payload


def _valid_chat_payload(payload: dict[str, Any]) -> bool:
    return "model" in payload and "messages" in payload


def _write_json(handler: BaseHTTPRequestHandler, body: dict[str, Any]) -> None:
    encoded = json.dumps(body).encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(encoded)))
    handler.end_headers()
    handler.wfile.write(encoded)
