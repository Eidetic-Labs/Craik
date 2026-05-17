"""Shared provider transport execution and retry handling."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from craik.runtime.auth import (
    AuthProfile,
    AuthProfileStore,
    CredentialHealthStatus,
    CredentialPool,
)
from craik.runtime.auth.operator import (
    active_operator_session,
    bind_operator_metadata,
    operator_identity_required,
)
from craik.runtime.auth.pool import PoolOutcome
from craik.runtime.providers.provider_models import (
    CredentialApprovalRequiredError,
    ProviderRuntimeAdapter,
    ProviderRuntimeError,
    ProviderRuntimeRequest,
    ProviderRuntimeResult,
)
from craik.runtime.providers.provider_runtime_support import _json_object_or_none, _retry_after
from craik.runtime.providers.provider_transport import ProviderTransportError


def execute_provider_request(
    adapter: ProviderRuntimeAdapter,
    request: ProviderRuntimeRequest,
    *,
    chunk_normalizer: Any | None = None,
    stream_callback: Callable[[str], None] | None = None,
) -> ProviderRuntimeResult:
    """Execute one provider request with retry and streaming normalization."""
    request = _request_with_operator_context(request)
    _enforce_credential_approval(adapter, request)
    if adapter.config.live_enabled:
        adapter.require_live_access()
    payload = adapter.build_payload(request)
    attempt = 0
    while True:
        try:
            result = _send_provider_request(
                adapter,
                request,
                payload,
                chunk_normalizer=chunk_normalizer,
                stream_callback=stream_callback,
            )
            _report_pool_outcome(adapter, "success")
            _mark_auth_profile_used(adapter, "ok")
            return result
        except ProviderTransportError as error:
            _report_pool_outcome(adapter, _pool_outcome_for_error(error))
            _mark_auth_profile_used(adapter, _profile_status_for_error(error))
            if (
                not _retryable_transport_error(adapter, error)
                or attempt >= adapter.config.max_retries
            ):
                raise
            attempt += 1
            _sleep_before_retry(adapter, error)


def _report_pool_outcome(adapter: ProviderRuntimeAdapter, outcome: PoolOutcome) -> None:
    if not adapter.config.credential_pool_id or not adapter.config.last_auth_profile_id:
        return

    CredentialPool.from_env().report(adapter.config.last_auth_profile_id, outcome)


def _mark_auth_profile_used(
    adapter: ProviderRuntimeAdapter,
    status: CredentialHealthStatus,
) -> None:
    if adapter.config.credential_pool_id or not adapter.config.auth_profile_id:
        return
    AuthProfileStore.from_env().mark_used(adapter.config.auth_profile_id, status)


def _profile_status_for_error(error: ProviderTransportError) -> CredentialHealthStatus:
    if error.status_code == 429:
        return "rate_limited"
    if error.status_code in {401, 403}:
        return "rejected"
    return "unknown"


def _pool_outcome_for_error(error: ProviderTransportError) -> PoolOutcome:
    if error.status_code == 429:
        return "rate_limited"
    if error.status_code in {401, 403}:
        return "rejected"
    return "failed"


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


def _request_with_operator_context(
    request: ProviderRuntimeRequest,
) -> ProviderRuntimeRequest:
    session = active_operator_session()
    if session is None:
        if operator_identity_required(request.metadata):
            raise ProviderRuntimeError("operator identity required; run craik login")
        return request
    request.metadata = bind_operator_metadata(request.metadata, session)
    return request


def _enforce_credential_approval(
    adapter: ProviderRuntimeAdapter,
    request: ProviderRuntimeRequest,
) -> None:
    if not adapter.config.live_enabled or not adapter.config.auth_profile_id:
        return
    profile = AuthProfileStore.from_env().get(adapter.config.auth_profile_id)
    if profile.last_used_at is not None or _profile_has_approval(profile, request):
        return
    run_id = str(request.metadata.get("run_id", "unknown"))
    raise CredentialApprovalRequiredError(
        "credential approval required; "
        f"run craik auth approve {profile.id} --run={run_id}"
    )


def _profile_has_approval(profile: AuthProfile, request: ProviderRuntimeRequest) -> bool:
    approval = profile.metadata.get("approval")
    if not isinstance(approval, dict):
        return False
    approved_run = approval.get("run_id")
    request_run = request.metadata.get("run_id")
    return not request_run or approved_run == request_run


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
