"""Provider runtime transport, receipt, and payload helper functions."""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Any

from craik.contracts.models import CapabilityReceipt, ModelProvider
from craik.runtime.auth import (
    AuthProfile,
    AuthProfileNotFoundError,
    AuthProfileStore,
    CredentialPool,
)
from craik.runtime.auth.sources import (
    EnvVarApiKeySource,
    source_for_auth_profile,
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
    return source_for_auth_profile(profile).headers_for(family)


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
    receipt = environment_receipt(
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
            **_receipt_operator_metadata(request),
            "payload": adapter.build_payload(request),
            "secret_ref_name": adapter.config.secret_ref_name,
        },
    )
    return receipt.model_copy(update=_receipt_auth_fields(adapter))


def _receipt_auth_fields(adapter: ProviderRuntimeAdapter) -> dict[str, str]:
    profile = _receipt_auth_profile(adapter)
    if profile is not None:
        return {
            "auth_profile_id": profile.id,
            "auth_kind": profile.kind.value,
            "auth_identity_hash": _auth_identity_hash(
                adapter.config.provider_family,
                profile.id,
                profile.kind.value,
                _auth_identity_basis(profile.metadata),
            ),
        }
    profile_id = adapter.config.last_auth_profile_id or adapter.config.auth_profile_id
    if profile_id:
        return {
            "auth_profile_id": profile_id,
            "auth_kind": "unknown",
            "auth_identity_hash": _auth_identity_hash(
                adapter.config.provider_family,
                profile_id,
                "unknown",
                "",
            ),
        }
    legacy_id = (
        f"{adapter.config.provider_family}:legacy-env"
        if adapter.config.secret_ref_name
        else f"{adapter.config.provider_family}:no-credential"
    )
    auth_kind = "api-key" if adapter.config.secret_ref_name else "marker"
    return {
        "auth_profile_id": legacy_id,
        "auth_kind": auth_kind,
        "auth_identity_hash": _auth_identity_hash(
            adapter.config.provider_family,
            legacy_id,
            auth_kind,
            adapter.config.secret_ref_name,
        ),
    }


def _receipt_auth_profile(adapter: ProviderRuntimeAdapter) -> AuthProfile | None:
    profile_id = adapter.config.last_auth_profile_id or adapter.config.auth_profile_id
    if not profile_id:
        return None
    try:
        return AuthProfileStore.from_env().get(profile_id)
    except AuthProfileNotFoundError:
        return None


def _auth_identity_basis(metadata: dict[str, Any]) -> str:
    for key in ("identity", "account", "email", "env_var", "ref", "source"):
        value = metadata.get(key)
        if isinstance(value, str) and value:
            return f"{key}:{value}"
    return ""


def _auth_identity_hash(
    family: str,
    profile_id: str,
    kind: str,
    basis: str,
) -> str:
    payload = json.dumps(
        {
            "family": family,
            "profile_id": profile_id,
            "kind": kind,
            "basis": basis,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _receipt_operator_metadata(request: ProviderRuntimeRequest) -> dict[str, Any]:
    metadata = request.metadata
    if not metadata.get("operator_subject"):
        return {}
    return {
        "operator_subject": metadata.get("operator_subject"),
        "operator_issuer": metadata.get("operator_issuer"),
        "operator_email": metadata.get("operator_email"),
        "operator_groups": metadata.get("operator_groups", []),
    }


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
