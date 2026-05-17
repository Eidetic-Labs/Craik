"""OpenAI and Anthropic provider runtime normalization."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, Literal, Protocol, cast

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel, ModelProvider
from craik.runtime.policy.redaction import redact
from craik.runtime.providers.provider_runtime_support import (
    _anthropic_message,
    _anthropic_tool,
    _anthropic_usage,
    _chat_completions_message,
    _chat_completions_tool,
    _chat_completions_tool_calls,
    _chat_completions_usage,
    _fixture_context,
    _json_object_or_none,
    _openai_message,
    _openai_tool,
    _openai_usage,
    _provider_base_url,
    _redacted_mapping,
    _retry_after,
    _transport_for_config,
)
from craik.runtime.providers.provider_runtime_support import (
    provider_runtime_receipt as provider_runtime_receipt,
)
from craik.runtime.providers.provider_transport import (
    FixtureTransport,
    ProviderFamily,
    ProviderTransport,
    ProviderTransportError,
)
from craik.runtime.secrets import SecretRef, SecretResolver

ProviderMessageRole = Literal["system", "user", "assistant", "tool"]

OPENAI_OFFICIAL_DOCS = (
    "https://platform.openai.com/docs/api-reference/responses",
    "https://platform.openai.com/docs/guides/streaming-responses",
    "https://platform.openai.com/docs/guides/structured-outputs",
    "https://platform.openai.com/docs/guides/tools",
)
ANTHROPIC_OFFICIAL_DOCS = (
    "https://docs.anthropic.com/en/api/messages",
    "https://docs.anthropic.com/claude/reference/messages-streaming",
    "https://docs.anthropic.com/en/docs/build-with-claude/tool-use",
    "https://docs.anthropic.com/en/docs/about-claude/models/all-models",
    "https://docs.anthropic.com/en/api/rate-limits",
)


class ProviderRuntimeError(RuntimeError):
    """Base error for provider runtime failures."""


class ProviderLiveAccessNotConfiguredError(ProviderRuntimeError):
    """Raised when live provider access is attempted without explicit configuration."""


class ProviderMessage(CraikModel):
    """Provider-neutral chat message."""

    role: ProviderMessageRole
    content: str


class ProviderTool(CraikModel):
    """Provider-neutral tool definition."""

    name: str
    description: str
    input_schema: dict[str, Any]


class ProviderRuntimeConfig(CraikModel):
    """Runtime configuration for one provider adapter."""

    provider_id: str
    provider_family: ProviderFamily
    model: str
    secret_ref_name: str
    base_url: str | None = None
    timeout_seconds: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    live_enabled: bool = False
    docs_verified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    docs_refs: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_runtime_config(self) -> ProviderRuntimeConfig:
        """Keep live access explicit and credentials reference-only."""
        if self.secret_ref_name and any(
            token in self.secret_ref_name.lower() for token in ("sk-", "token=", "key=")
        ):
            raise ValueError(
                "provider runtime secret_ref_name must not contain raw secret material"
            )
        expected_refs = (
            ANTHROPIC_OFFICIAL_DOCS
            if self.provider_family == "anthropic"
            else OPENAI_OFFICIAL_DOCS
        )
        missing = [ref for ref in expected_refs if ref not in self.docs_refs]
        if missing:
            raise ValueError(f"provider runtime docs_refs missing official refs: {missing}")
        return self

    def resolve_secret(self, resolver: SecretResolver) -> str:
        """Resolve the configured secret reference at request time."""
        if not self.secret_ref_name:
            return ""
        return resolver.resolve(SecretRef(env_var=self.secret_ref_name))


class ProviderRuntimeRequest(CraikModel):
    """Provider-neutral request used by runtime adapters."""

    messages: list[ProviderMessage] = Field(min_length=1)
    tools: list[ProviderTool] = Field(default_factory=list)
    structured_output_schema: dict[str, Any] | None = None
    structured_output_name: str = "craik_structured_output"
    max_output_tokens: int = Field(default=1024, ge=1)
    stream: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderRuntimeResult(CraikModel):
    """Provider-neutral response summary."""

    provider_id: str
    provider_family: ProviderFamily
    model: str
    text: str = ""
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    structured_output: dict[str, Any] | None = None
    structured_output_name: str | None = None
    usage: dict[str, int] = Field(default_factory=dict)
    response_id: str | None = None
    redacted: bool = True


class ProviderRuntimeChunk(CraikModel):
    """Provider-neutral streaming response chunk."""

    provider_id: str
    provider_family: ProviderFamily
    model: str
    text_delta: str = ""
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    usage: dict[str, int] = Field(default_factory=dict)
    response_id: str | None = None
    finish_reason: str | None = None
    redacted: bool = True


class ProviderRuntimeErrorDecision(CraikModel):
    """Provider-neutral retry decision for an API error."""

    provider_family: ProviderFamily
    status_code: int | None
    error_type: str | None
    retryable: bool
    retry_after_seconds: int | None = None
    reason: str


class ProviderRuntimeAdapter(Protocol):
    """Runtime adapter contract for provider-specific payloads."""

    config: ProviderRuntimeConfig
    transport: ProviderTransport

    def execute(
        self,
        request: ProviderRuntimeRequest,
        *,
        stream_callback: Callable[[str], None] | None = None,
    ) -> ProviderRuntimeResult:
        """Execute one provider request through the configured transport."""
        ...

    def build_payload(self, request: ProviderRuntimeRequest) -> dict[str, Any]:
        """Build a provider-specific request payload."""

    def normalize_response(self, response: dict[str, Any]) -> ProviderRuntimeResult:
        """Normalize a provider response payload."""

    def classify_error(
        self,
        *,
        status_code: int | None,
        error_type: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> ProviderRuntimeErrorDecision:
        """Classify whether an error is retryable."""

    def require_live_access(self) -> None:
        """Raise unless live API access was explicitly enabled."""


class OpenAIProviderAdapter:
    """OpenAI Responses API payload and response normalization."""

    def __init__(
        self,
        config: ProviderRuntimeConfig,
        transport: ProviderTransport | None = None,
    ) -> None:
        if config.provider_family != "openai":
            raise ValueError("OpenAIProviderAdapter requires provider_family='openai'")
        self.config = config
        self.transport = transport or FixtureTransport(family="openai", model=config.model)

    def build_payload(self, request: ProviderRuntimeRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "_path": "/v1/responses",
            "_fixture": _fixture_context(request),
            "model": self.config.model,
            "input": [_openai_message(message) for message in request.messages],
            "stream": request.stream,
            "metadata": _redacted_mapping(request.metadata),
        }
        if request.tools:
            payload["tools"] = [_openai_tool(tool) for tool in request.tools]
            payload["tool_choice"] = "auto"
        if request.structured_output_schema is not None:
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": request.structured_output_name,
                    "schema": request.structured_output_schema,
                    "strict": True,
                }
            }
        if request.max_output_tokens:
            payload["max_output_tokens"] = request.max_output_tokens
        return payload

    def execute(
        self,
        request: ProviderRuntimeRequest,
        *,
        stream_callback: Callable[[str], None] | None = None,
    ) -> ProviderRuntimeResult:
        """Execute one OpenAI Responses request through the configured transport."""
        return _execute_provider_request(self, request, stream_callback=stream_callback)

    def normalize_response(self, response: dict[str, Any]) -> ProviderRuntimeResult:
        output = response.get("output", [])
        text_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        for item in output if isinstance(output, list) else []:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "function_call":
                tool_calls.append(
                    {
                        "id": item.get("id"),
                        "call_id": item.get("call_id"),
                        "name": item.get("name"),
                        "arguments": redact(item.get("arguments", "")).value,
                    }
                )
            for content in item.get("content", []):
                if isinstance(content, dict) and content.get("type") == "output_text":
                    text_parts.append(str(content.get("text", "")))
        usage = _openai_usage(response.get("usage", {}))
        return ProviderRuntimeResult(
            provider_id=self.config.provider_id,
            provider_family="openai",
            model=str(response.get("model", self.config.model)),
            text=str(response.get("output_text") or "".join(text_parts)),
            tool_calls=tool_calls,
            usage=usage,
            response_id=str(response.get("id")) if response.get("id") else None,
        )

    def classify_error(
        self,
        *,
        status_code: int | None,
        error_type: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> ProviderRuntimeErrorDecision:
        retryable = status_code in {408, 409, 429, 500, 502, 503, 504}
        return ProviderRuntimeErrorDecision(
            provider_family="openai",
            status_code=status_code,
            error_type=error_type,
            retryable=retryable,
            retry_after_seconds=_retry_after(headers),
            reason="retryable OpenAI API condition"
            if retryable
            else "non-retryable OpenAI API condition",
        )

    def require_live_access(self) -> None:
        if not self.config.live_enabled:
            raise ProviderLiveAccessNotConfiguredError(
                "OpenAI live access requires live_enabled=true and an external secret resolver"
            )


class AnthropicProviderAdapter:
    """Anthropic Messages API payload and response normalization."""

    def __init__(
        self,
        config: ProviderRuntimeConfig,
        transport: ProviderTransport | None = None,
    ) -> None:
        if config.provider_family != "anthropic":
            raise ValueError("AnthropicProviderAdapter requires provider_family='anthropic'")
        self.config = config
        self.transport = transport or FixtureTransport(family="anthropic", model=config.model)

    def build_payload(self, request: ProviderRuntimeRequest) -> dict[str, Any]:
        system_messages = [
            message.content for message in request.messages if message.role == "system"
        ]
        chat_messages = [message for message in request.messages if message.role != "system"]
        payload: dict[str, Any] = {
            "_path": "/v1/messages",
            "_fixture": _fixture_context(request),
            "model": self.config.model,
            "max_tokens": request.max_output_tokens,
            "messages": [_anthropic_message(message) for message in chat_messages],
            "stream": request.stream,
            "metadata": {"user_id": str(request.metadata.get("user_id", "craik"))},
        }
        if system_messages:
            payload["system"] = "\n\n".join(system_messages)
        if request.tools:
            payload["tools"] = [_anthropic_tool(tool) for tool in request.tools]
            payload["tool_choice"] = {"type": "auto"}
        if request.structured_output_schema is not None:
            structured_tool = ProviderTool(
                name=request.structured_output_name,
                description="Emit the response as structured JSON matching the supplied schema.",
                input_schema=request.structured_output_schema,
            )
            payload["tools"] = [*payload.get("tools", []), _anthropic_tool(structured_tool)]
            payload["tool_choice"] = {
                "type": "tool",
                "name": request.structured_output_name,
            }
        return payload

    def execute(
        self,
        request: ProviderRuntimeRequest,
        *,
        stream_callback: Callable[[str], None] | None = None,
    ) -> ProviderRuntimeResult:
        """Execute one Anthropic Messages request through the configured transport."""
        return _execute_provider_request(self, request, stream_callback=stream_callback)

    def normalize_response(self, response: dict[str, Any]) -> ProviderRuntimeResult:
        text_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        structured_output: dict[str, Any] | None = None
        for block in response.get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                text_parts.append(str(block.get("text", "")))
            if block.get("type") == "tool_use":
                call = {
                    "id": block.get("id"),
                    "name": block.get("name"),
                    "input": redact(block.get("input", {})).value,
                }
                tool_calls.append(call)
                if block.get("name") == response.get(
                    "structured_output_name", "craik_structured_output"
                ) and isinstance(block.get("input"), dict):
                    structured_output = block["input"]
        return ProviderRuntimeResult(
            provider_id=self.config.provider_id,
            provider_family="anthropic",
            model=str(response.get("model", self.config.model)),
            text="".join(text_parts),
            tool_calls=tool_calls,
            structured_output=structured_output,
            usage=_anthropic_usage(response.get("usage", {})),
            response_id=str(response.get("id")) if response.get("id") else None,
        )

    def classify_error(
        self,
        *,
        status_code: int | None,
        error_type: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> ProviderRuntimeErrorDecision:
        retryable = status_code in {408, 429, 500, 502, 503, 504, 529}
        return ProviderRuntimeErrorDecision(
            provider_family="anthropic",
            status_code=status_code,
            error_type=error_type,
            retryable=retryable,
            retry_after_seconds=_retry_after(headers),
            reason=(
                "retryable Anthropic API condition"
                if retryable
                else "non-retryable Anthropic API condition"
            ),
        )

    def require_live_access(self) -> None:
        if not self.config.live_enabled:
            raise ProviderLiveAccessNotConfiguredError(
                "Anthropic live access requires live_enabled=true and an external secret resolver"
            )


class ChatCompletionsProviderAdapter:
    """OpenAI-compatible Chat Completions payload and response normalization."""

    def __init__(
        self,
        config: ProviderRuntimeConfig,
        transport: ProviderTransport | None = None,
    ) -> None:
        if config.provider_family != "chat_completions":
            raise ValueError(
                "ChatCompletionsProviderAdapter requires provider_family='chat_completions'"
            )
        self.config = config
        self.transport = transport or FixtureTransport(
            family="chat_completions", model=config.model
        )

    def build_payload(self, request: ProviderRuntimeRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "_path": "/v1/chat/completions",
            "_fixture": _fixture_context(request),
            "model": self.config.model,
            "messages": [_chat_completions_message(message) for message in request.messages],
            "stream": request.stream,
            "max_tokens": request.max_output_tokens,
        }
        if request.tools:
            payload["tools"] = [_chat_completions_tool(tool) for tool in request.tools]
            payload["tool_choice"] = "auto"
        if request.structured_output_schema is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": request.structured_output_name,
                    "schema": request.structured_output_schema,
                    "strict": True,
                },
            }
        return payload

    def execute(
        self,
        request: ProviderRuntimeRequest,
        *,
        stream_callback: Callable[[str], None] | None = None,
    ) -> ProviderRuntimeResult:
        """Execute one Chat Completions request through the configured transport."""
        return _execute_provider_request(
            self,
            request,
            chunk_normalizer=self.normalize_chunk,
            stream_callback=stream_callback,
        )

    def normalize_response(self, response: dict[str, Any]) -> ProviderRuntimeResult:
        choices = response.get("choices", [])
        message: dict[str, Any] = {}
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            raw_message = choices[0].get("message", {})
            if isinstance(raw_message, dict):
                message = raw_message
        content = str(message.get("content") or "")
        tool_calls = _chat_completions_tool_calls(message.get("tool_calls", []))
        return ProviderRuntimeResult(
            provider_id=self.config.provider_id,
            provider_family="chat_completions",
            model=str(response.get("model", self.config.model)),
            text=content,
            tool_calls=tool_calls,
            structured_output=_json_object_or_none(content),
            usage=_chat_completions_usage(response.get("usage", {})),
            response_id=str(response.get("id")) if response.get("id") else None,
        )

    def normalize_chunk(self, chunk: dict[str, Any]) -> ProviderRuntimeChunk:
        choices = chunk.get("choices", [])
        delta: dict[str, Any] = {}
        finish_reason: str | None = None
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            raw_delta = choices[0].get("delta", {})
            if isinstance(raw_delta, dict):
                delta = raw_delta
            raw_finish_reason = choices[0].get("finish_reason")
            finish_reason = str(raw_finish_reason) if raw_finish_reason is not None else None
        return ProviderRuntimeChunk(
            provider_id=self.config.provider_id,
            provider_family="chat_completions",
            model=str(chunk.get("model", self.config.model)),
            text_delta=str(delta.get("content") or ""),
            tool_calls=_chat_completions_tool_calls(delta.get("tool_calls", [])),
            usage=_chat_completions_usage(chunk.get("usage", {})),
            response_id=str(chunk.get("id")) if chunk.get("id") else None,
            finish_reason=finish_reason,
        )

    def classify_error(
        self,
        *,
        status_code: int | None,
        error_type: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> ProviderRuntimeErrorDecision:
        retryable = status_code in {408, 409, 429, 500, 502, 503, 504}
        return ProviderRuntimeErrorDecision(
            provider_family="chat_completions",
            status_code=status_code,
            error_type=error_type,
            retryable=retryable,
            retry_after_seconds=_retry_after(headers),
            reason=(
                "retryable Chat Completions API condition"
                if retryable
                else "non-retryable Chat Completions API condition"
            ),
        )

    def require_live_access(self) -> None:
        if not self.config.live_enabled:
            raise ProviderLiveAccessNotConfiguredError(
                "Chat Completions live access requires live_enabled=true and "
                "an external secret resolver"
            )


def adapter_for_provider(
    provider: ModelProvider, *, live_enabled: bool = False
) -> ProviderRuntimeAdapter:
    """Return the runtime adapter for a configured MVP provider."""
    family = provider.provider
    if family not in {"openai", "anthropic", "chat_completions"}:
        raise ValueError(f"provider {provider.id} is not an MVP live provider")
    model = str(provider.metadata.get("default_model", ""))
    if not model:
        raise ValueError(f"provider {provider.id} metadata requires default_model")
    secret_ref_name = provider.secret_ref_names[0] if provider.secret_ref_names else ""
    live_configured = live_enabled or bool(provider.metadata.get("live_enabled", False))
    config = ProviderRuntimeConfig(
        provider_id=provider.id,
        provider_family=cast(ProviderFamily, family),
        model=model,
        secret_ref_name=secret_ref_name,
        base_url=_provider_base_url(provider),
        timeout_seconds=float(provider.metadata.get("timeout_seconds", 30.0)),
        max_retries=int(provider.metadata.get("max_retries", 3)),
        live_enabled=live_configured,
        docs_refs=list(
            ANTHROPIC_OFFICIAL_DOCS if family == "anthropic" else OPENAI_OFFICIAL_DOCS
        ),
    )
    transport = _transport_for_config(config)
    if family == "openai":
        return OpenAIProviderAdapter(config, transport=transport)
    if family == "anthropic":
        return AnthropicProviderAdapter(config, transport=transport)
    return ChatCompletionsProviderAdapter(config, transport=transport)


def _execute_provider_request(
    adapter: ProviderRuntimeAdapter,
    request: ProviderRuntimeRequest,
    *,
    chunk_normalizer: Any | None = None,
    stream_callback: Callable[[str], None] | None = None,
) -> ProviderRuntimeResult:
    if adapter.config.live_enabled:
        adapter.require_live_access()
    payload = adapter.build_payload(request)
    attempt = 0
    while True:
        try:
            return _send_provider_request(
                adapter,
                request,
                payload,
                chunk_normalizer=chunk_normalizer,
                stream_callback=stream_callback,
            )
        except ProviderTransportError as error:
            if (
                not _retryable_transport_error(adapter, error)
                or attempt >= adapter.config.max_retries
            ):
                raise
            attempt += 1
            _sleep_before_retry(adapter, error)


def _send_provider_request(
    adapter: ProviderRuntimeAdapter,
    request: ProviderRuntimeRequest,
    payload: dict[str, Any],
    *,
    chunk_normalizer: Any | None = None,
    stream_callback: Callable[[str], None] | None = None,
) -> ProviderRuntimeResult:
    if not request.stream:
        chunks = list(adapter.transport.send(payload, stream=False))
        if not chunks:
            raise ProviderRuntimeError("provider transport returned no response chunks")
        return adapter.normalize_response(chunks[-1])
    if chunk_normalizer is None:
        chunks = list(adapter.transport.send(payload, stream=True))
        if not chunks:
            raise ProviderRuntimeError("provider transport returned no response chunks")
        return adapter.normalize_response(chunks[-1])
    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    usage: dict[str, int] = {}
    response_id: str | None = None
    model = adapter.config.model
    received_chunk = False
    for chunk in adapter.transport.send(payload, stream=True):
        received_chunk = True
        normalized = chunk_normalizer(chunk)
        text_parts.append(normalized.text_delta)
        if normalized.text_delta and stream_callback is not None:
            stream_callback(normalized.text_delta)
        tool_calls.extend(normalized.tool_calls)
        usage.update(normalized.usage)
        response_id = normalized.response_id or response_id
        model = normalized.model or model
    if not received_chunk:
        raise ProviderRuntimeError("provider transport returned no response chunks")
    text = "".join(text_parts)
    return ProviderRuntimeResult(
        provider_id=adapter.config.provider_id,
        provider_family=adapter.config.provider_family,
        model=model,
        text=text,
        tool_calls=tool_calls,
        structured_output=_json_object_or_none(text),
        usage=usage,
        response_id=response_id,
    )


def _retryable_transport_error(
    adapter: ProviderRuntimeAdapter,
    error: ProviderTransportError,
) -> bool:
    decision = adapter.classify_error(
        status_code=error.status_code,
        headers=error.headers,
    )
    return bool(error.retryable or decision.retryable)


def _sleep_before_retry(
    adapter: ProviderRuntimeAdapter,
    error: ProviderTransportError,
) -> None:
    cancel_event = getattr(adapter.transport, "cancel_event", None)
    if cancel_event is not None and cancel_event.is_set():
        raise ProviderTransportError("provider transport cancelled", retryable=False)
    retry_after = error.retry_after_seconds
    if retry_after is None:
        retry_after = _retry_after(error.headers)
    if retry_after is None:
        retry_after = 0
    delay = max(0, retry_after)
    if cancel_event is not None:
        if cancel_event.wait(delay):
            raise ProviderTransportError("provider transport cancelled", retryable=False)
        return
    time.sleep(delay)
