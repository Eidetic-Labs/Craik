"""OpenAI and Anthropic provider runtime normalization."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, Literal, Protocol, cast

from pydantic import Field, model_validator

from craik.contracts.models import CapabilityReceipt, CraikModel, ModelProvider
from craik.runtime.environment_receipts import EnvironmentReceiptContext, environment_receipt
from craik.runtime.http_transport import HTTPTransport
from craik.runtime.provider_transport import FixtureTransport, ProviderFamily, ProviderTransport
from craik.runtime.redaction import redact
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

    def execute(self, request: ProviderRuntimeRequest) -> ProviderRuntimeResult:
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

    def execute(self, request: ProviderRuntimeRequest) -> ProviderRuntimeResult:
        """Execute one OpenAI Responses request through the configured transport."""
        return _execute_provider_request(self, request)

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

    def execute(self, request: ProviderRuntimeRequest) -> ProviderRuntimeResult:
        """Execute one Anthropic Messages request through the configured transport."""
        return _execute_provider_request(self, request)

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

    def execute(self, request: ProviderRuntimeRequest) -> ProviderRuntimeResult:
        """Execute one Chat Completions request through the configured transport."""
        return _execute_provider_request(self, request, chunk_normalizer=self.normalize_chunk)

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
) -> ProviderRuntimeResult:
    if adapter.config.live_enabled:
        adapter.require_live_access()
    payload = adapter.build_payload(request)
    chunks = list(adapter.transport.send(payload, stream=request.stream))
    if not chunks:
        raise ProviderRuntimeError("provider transport returned no response chunks")
    if not request.stream:
        return adapter.normalize_response(chunks[-1])
    if chunk_normalizer is None:
        return adapter.normalize_response(chunks[-1])
    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    usage: dict[str, int] = {}
    response_id: str | None = None
    model = adapter.config.model
    for chunk in chunks:
        normalized = chunk_normalizer(chunk)
        text_parts.append(normalized.text_delta)
        tool_calls.extend(normalized.tool_calls)
        usage.update(normalized.usage)
        response_id = normalized.response_id or response_id
        model = normalized.model or model
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


def _transport_for_config(config: ProviderRuntimeConfig) -> ProviderTransport:
    if not config.live_enabled:
        return FixtureTransport(family=config.provider_family, model=config.model)
    if config.base_url is None:
        raise ProviderRuntimeError(f"provider {config.provider_id} requires base_url")
    return HTTPTransport(
        family=config.provider_family,
        base_url=config.base_url,
        headers_factory=lambda: _provider_headers(config),
        timeout_seconds=config.timeout_seconds,
    )


def _provider_headers(config: ProviderRuntimeConfig) -> dict[str, str]:
    if config.provider_family == "anthropic":
        headers = {
            "anthropic-version": "2023-06-01",
        }
        if config.secret_ref_name:
            headers["x-api-key"] = config.secret_ref_name
        return headers
    if config.secret_ref_name:
        return {"Authorization": f"Bearer {config.secret_ref_name}"}
    return {}


def _provider_base_url(provider: ModelProvider) -> str:
    configured = provider.metadata.get("base_url")
    if isinstance(configured, str) and configured:
        return configured
    if provider.provider == "anthropic":
        return "https://api.anthropic.com"
    return "https://api.openai.com"


def provider_runtime_receipt(
    *,
    adapter: ProviderRuntimeAdapter,
    request: ProviderRuntimeRequest,
    result: ProviderRuntimeResult,
    task_id: str,
    policy_envelope_id: str,
    receipt_id: str,
    actor: str,
) -> CapabilityReceipt:
    """Build a redacted receipt for one provider runtime action."""
    return environment_receipt(
        receipt_id=receipt_id,
        action="provider_action",
        context=EnvironmentReceiptContext(
            task_id=task_id,
            policy_envelope_id=policy_envelope_id,
            provider_id=adapter.config.provider_id,
            target_id=adapter.config.model,
        ),
        actor=actor,
        capability="model.chat",
        policy_profile="strict",
        status="passed",
        reason="Provider request normalized and redacted.",
        summary=f"{adapter.config.provider_family} provider call normalized.",
        metadata={
            "provider_family": adapter.config.provider_family,
            "model": result.model,
            "stream": request.stream,
            "tool_call_count": len(result.tool_calls),
            "usage": _receipt_usage(result.usage),
            "payload": adapter.build_payload(request),
            "secret_ref_name": adapter.config.secret_ref_name,
        },
    )


def _openai_message(message: ProviderMessage) -> dict[str, Any]:
    role = "developer" if message.role == "system" else message.role
    return {"role": role, "content": message.content}


def _openai_tool(tool: ProviderTool) -> dict[str, Any]:
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.input_schema,
        "strict": True,
    }


def _anthropic_message(message: ProviderMessage) -> dict[str, Any]:
    return {"role": message.role, "content": message.content}


def _anthropic_tool(tool: ProviderTool) -> dict[str, Any]:
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.input_schema,
    }


def _chat_completions_message(message: ProviderMessage) -> dict[str, Any]:
    return {"role": message.role, "content": message.content}


def _chat_completions_tool(tool: ProviderTool) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema,
        },
    }


def _chat_completions_tool_calls(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    tool_calls: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        function = item.get("function", {})
        function = function if isinstance(function, dict) else {}
        tool_calls.append(
            {
                "id": item.get("id"),
                "type": item.get("type"),
                "name": function.get("name"),
                "arguments": redact(function.get("arguments", "")).value,
            }
        )
    return tool_calls


def _fixture_context(request: ProviderRuntimeRequest) -> dict[str, str]:
    context: dict[str, str] = {}
    if "phase" in request.metadata:
        context["phase"] = str(request.metadata["phase"])
    if "status" in request.metadata:
        context["status"] = str(request.metadata["status"])
    if "response_id" in request.metadata:
        context["response_id"] = str(request.metadata["response_id"])
    elif "run_id" in request.metadata and "phase" in request.metadata:
        context["response_id"] = (
            f"provider_response_{request.metadata['run_id']}_{request.metadata['phase']}"
        )
    return context


def _openai_usage(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    return {
        "input_tokens": int(value.get("input_tokens", 0) or 0),
        "output_tokens": int(value.get("output_tokens", 0) or 0),
        "total_tokens": int(value.get("total_tokens", 0) or 0),
    }


def _anthropic_usage(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    input_tokens = int(value.get("input_tokens", 0) or 0)
    output_tokens = int(value.get("output_tokens", 0) or 0)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
    }


def _chat_completions_usage(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    prompt_tokens = int(value.get("prompt_tokens", 0) or 0)
    completion_tokens = int(value.get("completion_tokens", 0) or 0)
    total_tokens = int(value.get("total_tokens", prompt_tokens + completion_tokens) or 0)
    return {
        "input_tokens": prompt_tokens,
        "output_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


def _json_object_or_none(value: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _retry_after(headers: dict[str, str] | None) -> int | None:
    if not headers:
        return None
    for key, value in headers.items():
        if key.lower() == "retry-after" and value.isdigit():
            return int(value)
    return None


def _receipt_usage(usage: dict[str, int]) -> dict[str, int]:
    return {
        "input": usage.get("input_tokens", 0),
        "output": usage.get("output_tokens", 0),
        "total": usage.get("total_tokens", 0),
    }


def _redacted_mapping(value: dict[str, Any]) -> dict[str, Any]:
    redacted = redact(value).value
    if isinstance(redacted, dict):
        return redacted
    return {}
