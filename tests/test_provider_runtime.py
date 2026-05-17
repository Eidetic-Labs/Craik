import pytest
from pydantic import ValidationError

from craik.runtime.model_providers import default_model_provider_registry
from craik.runtime.provider_runtime import (
    ANTHROPIC_OFFICIAL_DOCS,
    OPENAI_OFFICIAL_DOCS,
    AnthropicProviderAdapter,
    OpenAIProviderAdapter,
    ProviderLiveAccessNotConfiguredError,
    ProviderMessage,
    ProviderRuntimeConfig,
    ProviderRuntimeRequest,
    ProviderTool,
    adapter_for_provider,
    provider_runtime_receipt,
)


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


def test_live_provider_access_requires_explicit_enablement() -> None:
    with pytest.raises(ProviderLiveAccessNotConfiguredError):
        _openai_adapter().require_live_access()
    with pytest.raises(ProviderLiveAccessNotConfiguredError):
        _anthropic_adapter().require_live_access()

    _openai_adapter(live_enabled=True).require_live_access()
    _anthropic_adapter(live_enabled=True).require_live_access()


def test_adapter_for_default_mvp_providers_uses_verified_docs_and_secret_references() -> None:
    registry = default_model_provider_registry()

    openai = adapter_for_provider(registry.require("provider_openai"))
    anthropic = adapter_for_provider(registry.require("provider_anthropic"))

    assert isinstance(openai, OpenAIProviderAdapter)
    assert openai.config.secret_ref_name == "CRAIK_OPENAI_API_KEY"
    assert openai.config.docs_refs == list(OPENAI_OFFICIAL_DOCS)
    assert isinstance(anthropic, AnthropicProviderAdapter)
    assert anthropic.config.secret_ref_name == "CRAIK_ANTHROPIC_API_KEY"
    assert anthropic.config.docs_refs == list(ANTHROPIC_OFFICIAL_DOCS)


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
