from __future__ import annotations

import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib import error, request

import pytest

from craik.runtime.http_transport import HTTPTransport
from craik.runtime.provider_runtime import (
    OPENAI_OFFICIAL_DOCS,
    ChatCompletionsProviderAdapter,
    ProviderMessage,
    ProviderRuntimeConfig,
    ProviderRuntimeRequest,
)
from craik.runtime.provider_transport import ProviderFamily

CASSETTE_PATH = (
    Path(__file__).parents[1] / "fixtures" / "cassettes" / "chat_completions_recorded.json"
)


@pytest.mark.integration
def test_recorded_chat_completions_round_trip_returns_model_text() -> None:
    adapter = ChatCompletionsProviderAdapter(
        ProviderRuntimeConfig(
            provider_id="provider_recorded_openai_compatible",
            provider_family="chat_completions",
            model="recorded-openai-compatible",
            secret_ref_name="",
            docs_refs=list(OPENAI_OFFICIAL_DOCS),
        ),
        transport=RecordedChatCompletionsTransport(CASSETTE_PATH),
    )

    result = adapter.execute(
        ProviderRuntimeRequest(
            messages=[
                ProviderMessage(
                    role="user",
                    content="Name one concrete Craik provider integration finding.",
                )
            ],
            max_output_tokens=64,
        )
    )

    assert result.text
    assert "fixture" not in result.text.lower()
    assert "OpenAI-compatible adapter" in result.text
    assert result.usage == {"input_tokens": 12, "output_tokens": 15, "total_tokens": 27}


@pytest.mark.integration
@pytest.mark.live
def test_local_openai_compatible_live_round_trip_returns_model_text() -> None:
    if os.environ.get("CRAIK_RUN_LIVE_TESTS") != "1":
        pytest.skip("set CRAIK_RUN_LIVE_TESTS=1 to run optional live provider tests")
    base_url = os.environ.get("CRAIK_LOCAL_OPENAI_BASE_URL", "http://localhost:11434/v1")
    if not _local_provider_reachable(base_url):
        pytest.skip(f"local OpenAI-compatible provider is not reachable at {base_url}")

    model = os.environ.get("CRAIK_LOCAL_OPENAI_MODEL", "llama3.2")
    adapter = ChatCompletionsProviderAdapter(
        ProviderRuntimeConfig(
            provider_id="provider_local_openai_compatible",
            provider_family="chat_completions",
            model=model,
            secret_ref_name="",
            base_url=base_url,
            live_enabled=True,
            docs_refs=list(OPENAI_OFFICIAL_DOCS),
        ),
        transport=HTTPTransport(
            family="chat_completions",
            base_url=base_url,
            headers_factory=dict,
            timeout_seconds=30,
        ),
    )

    result = adapter.execute(
        ProviderRuntimeRequest(
            messages=[ProviderMessage(role="user", content="Reply with one short sentence.")],
            max_output_tokens=64,
        )
    )

    assert result.text.strip()
    assert "fixture" not in result.text.lower()


class RecordedChatCompletionsTransport:
    def __init__(self, cassette_path: Path) -> None:
        self._cassette_path = cassette_path

    @property
    def family(self) -> ProviderFamily:
        return "chat_completions"

    def send(self, payload: dict[str, Any], *, stream: bool) -> Iterator[dict[str, Any]]:
        assert stream is False
        cassette = json.loads(self._cassette_path.read_text())
        expected = cassette["request"]
        body_payload = {key: value for key, value in payload.items() if not key.startswith("_")}
        assert body_payload == expected
        yield cassette["response"]


def _local_provider_reachable(base_url: str) -> bool:
    url = base_url.rstrip("/")
    if url.endswith("/v1"):
        url = f"{url}/models"
    else:
        url = f"{url}/v1/models"
    try:
        with request.urlopen(url, timeout=2) as response:
            return 200 <= response.status < 300
    except (TimeoutError, error.URLError):
        return False
