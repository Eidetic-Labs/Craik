import pytest
from pydantic import ValidationError

from craik.contracts.models import ModelProvider
from craik.runtime.providers.model_providers import default_model_provider_registry
from craik.runtime.providers.provider_runtime import (
    ANTHROPIC_OFFICIAL_DOCS,
    OPENAI_OFFICIAL_DOCS,
    AnthropicProviderAdapter,
    ChatCompletionsProviderAdapter,
    OpenAIProviderAdapter,
    ProviderLiveAccessNotConfiguredError,
    ProviderMessage,
    ProviderRuntimeConfig,
    ProviderRuntimeRequest,
    ProviderTool,
    adapter_for_provider,
    provider_runtime_receipt,
)
from craik.runtime.providers.provider_transport import (
    FixtureTransport,
    ProviderFamily,
    ProviderTransport,
)
from craik.runtime.secrets import SecretResolver


def _openai_adapter(*, live_enabled: bool = False) -> OpenAIProviderAdapter:
    return OpenAIProviderAdapter(
        ProviderRuntimeConfig(
            provider_id="provider_openai",
            provider_family="openai",
            model="gpt-5.2",
            secret_ref_name="CRAIK_OPENAI_API_KEY",
            live_enabled=live_enabled,
            docs_refs=list(OPENAI_OFFICIAL_DOCS),
        )
    )


def _anthropic_adapter(*, live_enabled: bool = False) -> AnthropicProviderAdapter:
    return AnthropicProviderAdapter(
        ProviderRuntimeConfig(
            provider_id="provider_anthropic",
            provider_family="anthropic",
            model="claude-sonnet-4-20250514",
            secret_ref_name="CRAIK_ANTHROPIC_API_KEY",
            live_enabled=live_enabled,
            docs_refs=list(ANTHROPIC_OFFICIAL_DOCS),
        )
    )


def _chat_completions_adapter(
    *, live_enabled: bool = False
) -> ChatCompletionsProviderAdapter:
    return ChatCompletionsProviderAdapter(
        ProviderRuntimeConfig(
            provider_id="provider_openai_chat",
            provider_family="chat_completions",
            model="gpt-5.2",
            secret_ref_name="CRAIK_OPENAI_API_KEY",
            live_enabled=live_enabled,
            docs_refs=list(OPENAI_OFFICIAL_DOCS),
        )
    )


def _request() -> ProviderRuntimeRequest:
    return ProviderRuntimeRequest(
        messages=[
            ProviderMessage(role="system", content="Follow the policy."),
            ProviderMessage(role="user", content="Create a plan."),
        ],
        tools=[
            ProviderTool(
                name="lookup_case",
                description="Lookup case metadata.",
                input_schema={
                    "type": "object",
                    "properties": {"case_id": {"type": "string"}},
                    "required": ["case_id"],
                },
            )
        ],
        structured_output_schema={
            "type": "object",
            "properties": {"answer": {"type": "string"}},
            "required": ["answer"],
            "additionalProperties": False,
        },
        stream=True,
        metadata={"user_id": "case-user", "api_key": "sk-test-secret"},
    )


def test_openai_payload_supports_messages_tools_structured_output_and_redaction() -> None:
    payload = _openai_adapter().build_payload(_request())

    assert payload["model"] == "gpt-5.2"
    assert payload["stream"] is True
    assert payload["input"][0] == {"role": "developer", "content": "Follow the policy."}
    assert payload["tools"][0]["type"] == "function"
    assert payload["tools"][0]["strict"] is True
    assert payload["tool_choice"] == "auto"
    assert payload["text"]["format"]["type"] == "json_schema"
    assert payload["text"]["format"]["strict"] is True
    assert payload["metadata"]["api_key"] == "[REDACTED]"


def test_openai_response_normalizes_text_tool_calls_usage_and_retry_decisions() -> None:
    adapter = _openai_adapter()
    result = adapter.normalize_response(
        {
            "id": "resp_123",
            "model": "gpt-5.2",
            "output": [
                {"type": "message", "content": [{"type": "output_text", "text": "Done"}]},
                {
                    "type": "function_call",
                    "id": "fc_123",
                    "call_id": "call_123",
                    "name": "lookup_case",
                    "arguments": '{"token":"sk-test-secret"}',
                },
            ],
            "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        }
    )
    retryable = adapter.classify_error(status_code=429, headers={"retry-after": "7"})
    terminal = adapter.classify_error(status_code=400)

    assert result.text == "Done"
    assert result.tool_calls[0]["arguments"] == '{"token":"[REDACTED]"}'
    assert result.usage == {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}
    assert retryable.retryable is True
    assert retryable.retry_after_seconds == 7
    assert terminal.retryable is False


def test_anthropic_payload_supports_messages_tools_structured_output_and_secret_refs() -> None:
    payload = _anthropic_adapter().build_payload(_request())

    assert payload["model"] == "claude-sonnet-4-20250514"
    assert payload["stream"] is True
    assert payload["system"] == "Follow the policy."
    assert payload["messages"] == [{"role": "user", "content": "Create a plan."}]
    assert payload["tools"][0]["name"] == "lookup_case"
    assert payload["tools"][0]["input_schema"]["required"] == ["case_id"]
    assert payload["tools"][1]["name"] == "craik_structured_output"
    assert payload["tool_choice"] == {"type": "tool", "name": "craik_structured_output"}
    assert payload["metadata"] == {"user_id": "case-user"}


def test_anthropic_response_normalizes_text_tool_calls_usage_and_retry_decisions() -> None:
    adapter = _anthropic_adapter()
    result = adapter.normalize_response(
        {
            "id": "msg_123",
            "model": "claude-sonnet-4-20250514",
            "content": [
                {"type": "text", "text": "Done"},
                {
                    "type": "tool_use",
                    "id": "toolu_123",
                    "name": "craik_structured_output",
                    "input": {"answer": "ok", "token": "sk-test-secret"},
                },
            ],
            "usage": {"input_tokens": 11, "output_tokens": 6},
        }
    )
    retryable = adapter.classify_error(status_code=529, headers={"Retry-After": "11"})
    terminal = adapter.classify_error(status_code=400)

    assert result.text == "Done"
    assert result.structured_output == {"answer": "ok", "token": "sk-test-secret"}
    assert result.tool_calls[0]["input"] == {"answer": "ok", "token": "[REDACTED]"}
    assert result.usage == {"input_tokens": 11, "output_tokens": 6, "total_tokens": 17}
    assert retryable.retryable is True
    assert retryable.retry_after_seconds == 11
    assert terminal.retryable is False


def test_chat_completions_payload_supports_messages_tools_and_structured_output() -> None:
    payload = _chat_completions_adapter().build_payload(_request())

    assert payload["model"] == "gpt-5.2"
    assert payload["stream"] is True
    assert payload["max_tokens"] == 1024
    assert payload["messages"][0] == {"role": "system", "content": "Follow the policy."}
    assert payload["tools"][0] == {
        "type": "function",
        "function": {
            "name": "lookup_case",
            "description": "Lookup case metadata.",
            "parameters": {
                "type": "object",
                "properties": {"case_id": {"type": "string"}},
                "required": ["case_id"],
            },
        },
    }
    assert payload["tool_choice"] == "auto"
    assert payload["response_format"]["type"] == "json_schema"
    assert payload["response_format"]["json_schema"]["strict"] is True


def test_chat_completions_payload_omits_tools_and_structured_output_when_absent() -> None:
    request = ProviderRuntimeRequest(
        messages=[ProviderMessage(role="user", content="Create a plan.")],
    )

    payload = _chat_completions_adapter().build_payload(request)

    assert payload["messages"] == [{"role": "user", "content": "Create a plan."}]
    assert "tools" not in payload
    assert "response_format" not in payload


def test_chat_completions_response_normalizes_content_tool_calls_usage() -> None:
    adapter = _chat_completions_adapter()
    content = adapter.normalize_response(
        {
            "id": "chatcmpl_123",
            "model": "gpt-5.2",
            "choices": [{"message": {"role": "assistant", "content": "Done"}}],
            "usage": {
                "prompt_tokens": 13,
                "completion_tokens": 8,
                "total_tokens": 21,
            },
        }
    )
    tool_call = adapter.normalize_response(
        {
            "id": "chatcmpl_456",
            "model": "gpt-5.2",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": '{"answer":"ok"}',
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {
                                    "name": "lookup_case",
                                    "arguments": '{"token":"sk-test-secret"}',
                                },
                            }
                        ],
                    }
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3},
        }
    )
    retryable = adapter.classify_error(status_code=429, headers={"Retry-After": "9"})
    server_error = adapter.classify_error(status_code=503)
    terminal = adapter.classify_error(status_code=400)

    assert content.text == "Done"
    assert content.usage == {"input_tokens": 13, "output_tokens": 8, "total_tokens": 21}
    assert tool_call.structured_output == {"answer": "ok"}
    assert tool_call.tool_calls == [
        {
            "id": "call_123",
            "type": "function",
            "name": "lookup_case",
            "arguments": '{"token":"[REDACTED]"}',
        }
    ]
    assert tool_call.usage == {"input_tokens": 5, "output_tokens": 3, "total_tokens": 8}
    assert retryable.retryable is True
    assert retryable.retry_after_seconds == 9
    assert server_error.retryable is True
    assert terminal.retryable is False


def test_chat_completions_stream_chunk_normalizes_delta_content_and_tool_calls() -> None:
    chunk = _chat_completions_adapter().normalize_chunk(
        {
            "id": "chatcmpl_chunk",
            "model": "gpt-5.2",
            "choices": [
                {
                    "delta": {
                        "content": "Hel",
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {
                                    "name": "lookup_case",
                                    "arguments": '{"case_id":"case_1"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": None,
                }
            ],
        }
    )

    assert chunk.text_delta == "Hel"
    assert chunk.tool_calls[0]["name"] == "lookup_case"
    assert chunk.response_id == "chatcmpl_chunk"


def test_chat_completions_stream_execute_emits_callback_chunks() -> None:
    chunks: list[str] = []
    adapter = ChatCompletionsProviderAdapter(
        _chat_completions_adapter().config,
        transport=FixtureTransport(
            family="chat_completions",
            model="gpt-5.2",
            response_id="chatcmpl_stream_fixture",
            stream_chunks=("Hel", "lo", "!"),
        ),
    )

    result = adapter.execute(
        ProviderRuntimeRequest(
            messages=[ProviderMessage(role="user", content="Say hello.")],
            stream=True,
        ),
        stream_callback=chunks.append,
    )

    assert chunks == ["Hel", "lo", "!"]
    assert result.text == "Hello!"
    assert result.response_id == "chatcmpl_stream_fixture"
    assert result.usage == {"input_tokens": 20, "output_tokens": 3, "total_tokens": 23}


def test_live_provider_access_requires_explicit_enablement() -> None:
    with pytest.raises(ProviderLiveAccessNotConfiguredError):
        _openai_adapter().require_live_access()
    with pytest.raises(ProviderLiveAccessNotConfiguredError):
        _anthropic_adapter().require_live_access()
    with pytest.raises(ProviderLiveAccessNotConfiguredError):
        _chat_completions_adapter().require_live_access()

    _openai_adapter(live_enabled=True).require_live_access()
    _anthropic_adapter(live_enabled=True).require_live_access()
    _chat_completions_adapter(live_enabled=True).require_live_access()


@pytest.mark.parametrize(
    ("adapter", "family"),
    [
        (_openai_adapter(), "openai"),
        (_anthropic_adapter(), "anthropic"),
    ],
)
def test_fixture_transport_yields_provider_family_response(
    adapter: OpenAIProviderAdapter | AnthropicProviderAdapter,
    family: ProviderFamily,
) -> None:
    transport: ProviderTransport = FixtureTransport(
        family=family,
        model=adapter.config.model,
        response_id="provider_response_fixture_plan",
        phase="plan",
        status="completed",
    )

    chunks = list(transport.send(adapter.build_payload(_request()), stream=False))
    result = adapter.normalize_response(chunks[0])

    assert len(chunks) == 1
    assert result.response_id == "provider_response_fixture_plan"
    assert result.model == adapter.config.model
    assert result.text == f"{family} fixture completed plan with status completed."


def test_adapter_for_default_mvp_providers_uses_verified_docs_and_secret_references() -> None:
    registry = default_model_provider_registry()

    openai = adapter_for_provider(registry.require("provider_openai"))
    anthropic = adapter_for_provider(registry.require("provider_anthropic"))
    openai_responses = adapter_for_provider(registry.require("provider_openai_responses"))
    anthropic_messages = adapter_for_provider(
        registry.require("provider_anthropic_messages")
    )
    openai_chat = adapter_for_provider(registry.require("provider_openai_chat"))
    local_openai_compatible = adapter_for_provider(
        registry.require("provider_local_openai_compatible")
    )

    assert isinstance(openai, OpenAIProviderAdapter)
    assert openai.config.secret_ref_name == "CRAIK_OPENAI_API_KEY"
    assert openai.config.docs_refs == list(OPENAI_OFFICIAL_DOCS)
    assert isinstance(anthropic, AnthropicProviderAdapter)
    assert anthropic.config.secret_ref_name == "CRAIK_ANTHROPIC_API_KEY"
    assert anthropic.config.docs_refs == list(ANTHROPIC_OFFICIAL_DOCS)
    assert isinstance(openai_responses, OpenAIProviderAdapter)
    assert openai_responses.config.secret_ref_name == "OPENAI_API_KEY"
    assert openai_responses.config.base_url == "https://api.openai.com"
    assert isinstance(anthropic_messages, AnthropicProviderAdapter)
    assert anthropic_messages.config.secret_ref_name == "ANTHROPIC_API_KEY"
    assert anthropic_messages.config.base_url == "https://api.anthropic.com"
    assert isinstance(openai_chat, ChatCompletionsProviderAdapter)
    assert openai_chat.config.secret_ref_name == "OPENAI_API_KEY"
    assert openai_chat.config.base_url == "https://api.openai.com"
    assert isinstance(local_openai_compatible, ChatCompletionsProviderAdapter)
    assert local_openai_compatible.config.secret_ref_name == ""
    assert local_openai_compatible.config.base_url == "http://localhost:11434/v1"


def test_adapter_for_provider_dispatches_chat_completions_family() -> None:
    provider = ModelProvider.model_validate(
        {
            "id": "provider_openai_chat",
            "name": "OpenAI Chat Completions",
            "provider": "chat_completions",
            "modes": ["chat", "tool", "runner"],
            "capabilities": [
                {
                    "name": "model.chat",
                    "mode": "chat",
                    "description": "Chat completions request execution.",
                    "grant_required": True,
                }
            ],
            "trust_boundary": "third-party",
            "config_refs": ["OPENAI_BASE_URL"],
            "secret_ref_names": ["OPENAI_API_KEY"],
            "budget_ref": "budget_openai_monthly",
            "quota_ref": "quota_openai_daily",
            "runtime_path": (
                "craik.runtime.providers.provider_runtime.ChatCompletionsProviderAdapter"
            ),
            "metadata": {
                "default_model": "gpt-5.2",
                "docs_verified": "2026-05-17",
            },
            "docs": ["docs/reference/model-providers.md", *OPENAI_OFFICIAL_DOCS],
            "created_at": "2026-05-17T08:00:00Z",
        }
    )

    adapter = adapter_for_provider(provider)

    assert isinstance(adapter, ChatCompletionsProviderAdapter)
    assert adapter.config.provider_family == "chat_completions"
    assert adapter.config.secret_ref_name == "OPENAI_API_KEY"


def test_provider_runtime_rejects_raw_secret_config_and_missing_docs() -> None:
    with pytest.raises(ValidationError, match="raw secret material"):
        ProviderRuntimeConfig(
            provider_id="provider_openai",
            provider_family="openai",
            model="gpt-5.2",
            secret_ref_name="sk-raw-secret",
            docs_refs=list(OPENAI_OFFICIAL_DOCS),
        )
    with pytest.raises(ValidationError, match="missing official refs"):
        ProviderRuntimeConfig(
            provider_id="provider_openai",
            provider_family="openai",
            model="gpt-5.2",
            secret_ref_name="CRAIK_OPENAI_API_KEY",
            docs_refs=["docs/reference/model-providers.md"],
        )


def test_provider_runtime_config_allows_no_secret_for_local_providers() -> None:
    config = ProviderRuntimeConfig(
        provider_id="provider_local_openai_compatible",
        provider_family="chat_completions",
        model="llama3.2",
        secret_ref_name="",
        docs_refs=list(OPENAI_OFFICIAL_DOCS),
    )

    assert config.resolve_secret(SecretResolver()) == ""


def test_provider_runtime_config_resolves_secret_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CRAIK_OPENAI_API_KEY", "resolved-secret")

    assert _openai_adapter().config.resolve_secret(SecretResolver()) == "resolved-secret"


def test_provider_runtime_receipt_keeps_safe_metadata_and_drops_payload_and_secret_ref() -> None:
    adapter = _openai_adapter()
    request = _request()
    result = adapter.normalize_response(
        {
            "id": "resp_123",
            "model": "gpt-5.2",
            "output_text": "Done",
            "usage": {"input_tokens": 3, "output_tokens": 2, "total_tokens": 5},
        }
    )

    receipt = provider_runtime_receipt(
        adapter=adapter,
        request=request,
        result=result,
        task_id="task_provider_runtime",
        policy_envelope_id="policy_provider_runtime",
        receipt_id="receipt_provider_runtime",
        actor="agent:codex",
    )

    assert receipt.target == "provider_action:provider_openai"
    assert receipt.result.metadata["provider_family"] == "openai"
    assert receipt.result.metadata["usage"] == {
        "input": 3,
        "output": 2,
        "total": 5,
    }
    assert receipt.result.metadata["tool_call_count"] == 0
    assert "payload" not in receipt.result.metadata
    assert "secret_ref_name" not in receipt.result.metadata
