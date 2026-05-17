"""Provider runtime transport, receipt, and payload helper functions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from craik.contracts.models import CapabilityReceipt, ModelProvider
from craik.runtime.auth import (
    AuthProfile,
    AuthProfileStore,
    CredentialKind,
    CredentialPool,
    CredentialSource,
)
from craik.runtime.auth.sources import (
    DEFAULT_CLAUDE_CREDENTIALS_PATH,
    CLIBridgeCredentialSource,
    EnvVarApiKeySource,
    EnvVarSecretManager,
    FileSecretManager,
    LocalCLICredentialSource,
    SecretRefCredentialSource,
)
from craik.runtime.environment_receipts import EnvironmentReceiptContext, environment_receipt
from craik.runtime.policy.redaction import redact
from craik.runtime.providers.http_transport import HTTPTransport
from craik.runtime.providers.provider_transport import (
    FixtureTransport,
    ProviderFamily,
    ProviderTransport,
)

if TYPE_CHECKING:
    from craik.runtime.providers.provider_runtime import (
        ProviderMessage,
        ProviderRuntimeAdapter,
        ProviderRuntimeConfig,
        ProviderRuntimeRequest,
        ProviderRuntimeResult,
        ProviderTool,
    )

def _transport_for_config(config: ProviderRuntimeConfig) -> ProviderTransport:
    if not config.live_enabled:
        return FixtureTransport(family=config.provider_family, model=config.model)
    if config.base_url is None:
        from craik.runtime.providers.provider_runtime import ProviderRuntimeError

        raise ProviderRuntimeError(f"provider {config.provider_id} requires base_url")
    return HTTPTransport(
        family=config.provider_family,
        base_url=config.base_url,
        headers_factory=lambda: _provider_headers(config),
        timeout_seconds=config.timeout_seconds,
    )


def _provider_headers(config: ProviderRuntimeConfig) -> dict[str, str]:
    if config.credential_pool_id:
        pool = CredentialPool.from_env()
        profile = pool.select_from_pool(config.credential_pool_id)
        if profile.provider_family != config.provider_family:
            raise ValueError("credential pool selected profile for the wrong provider family")
        config.last_auth_profile_id = profile.id
        return _headers_for_auth_profile(profile, config.provider_family)
    if config.auth_profile_id:
        profile = AuthProfileStore.from_env().get(config.auth_profile_id)
        config.last_auth_profile_id = profile.id
        return _headers_for_auth_profile(profile, config.provider_family)
    return EnvVarApiKeySource(config.secret_ref_name).headers_for(config.provider_family)


def _headers_for_auth_profile(
    profile: AuthProfile,
    family: ProviderFamily,
) -> dict[str, str]:
    return _source_for_auth_profile(profile).headers_for(family)


def _source_for_auth_profile(profile: AuthProfile) -> CredentialSource:
    if profile.kind is CredentialKind.API_KEY:
        env_var = profile.metadata.get("env_var")
        env_var = env_var if isinstance(env_var, str) else ""
        return EnvVarApiKeySource(env_var)
    if profile.kind is CredentialKind.OAUTH_TOKEN and profile.metadata.get("source") == "local-cli":
        credentials_path = profile.metadata.get("credentials_path")
        refresh_endpoint = profile.metadata.get("refresh_endpoint")
        client_id = profile.metadata.get("client_id")
        return LocalCLICredentialSource(
            credentials_path=Path(credentials_path)
            if isinstance(credentials_path, str)
            else DEFAULT_CLAUDE_CREDENTIALS_PATH,
            refresh_endpoint=refresh_endpoint if isinstance(refresh_endpoint, str) else None,
            client_id=client_id if isinstance(client_id, str) else None,
        )
    if profile.kind is CredentialKind.SECRET_REF:
        ref = profile.metadata.get("ref")
        manager = profile.metadata.get("manager", "env")
        if not isinstance(ref, str):
            raise ValueError("secret-ref auth profile requires metadata.ref")
        secret_manager = FileSecretManager() if manager == "file" else EnvVarSecretManager()
        return SecretRefCredentialSource(ref=ref, manager=secret_manager)
    if profile.kind is CredentialKind.CLI_BRIDGE:
        command = profile.metadata.get("command")
        extractor = profile.metadata.get("token_extractor", "stdout_json")
        key_path = profile.metadata.get("key_path", ["token"])
        if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
            raise ValueError("cli-bridge auth profile requires metadata.command")
        if extractor not in {"stdout_json", "stdout_line", "credentials_file"}:
            raise ValueError("cli-bridge auth profile has unsupported token_extractor")
        path = profile.metadata.get("credentials_file_path")
        return CLIBridgeCredentialSource(
            command=tuple(command),
            token_extractor=extractor,
            key_path=tuple(item for item in key_path if isinstance(item, str))
            if isinstance(key_path, list)
            else ("token",),
            credentials_file_path=Path(path) if isinstance(path, str) else None,
        )
    raise ValueError(f"unsupported auth profile kind/source: {profile.kind.value}")


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
