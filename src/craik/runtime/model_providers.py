"""Model provider registry helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from craik.contracts.models import ModelProvider


class ModelProviderRegistryError(RuntimeError):
    """Base error for model provider registry failures."""


class ModelProviderNotFoundError(ModelProviderRegistryError):
    """Raised when a provider id is not registered."""


class DuplicateModelProviderError(ModelProviderRegistryError):
    """Raised when a provider id is registered twice."""


class ModelProviderRegistry:
    """In-memory registry for model providers and runtime execution paths."""

    def __init__(self, providers: list[ModelProvider] | None = None) -> None:
        self._providers: dict[str, ModelProvider] = {}
        for provider in providers or []:
            self.register(provider)

    def register(self, provider: ModelProvider) -> ModelProvider:
        """Register one provider by stable id."""
        if provider.id in self._providers:
            raise DuplicateModelProviderError(f"provider already registered: {provider.id}")
        self._providers[provider.id] = provider
        return provider

    def get(self, provider_id: str) -> ModelProvider | None:
        """Return one provider by id, if registered."""
        return self._providers.get(provider_id)

    def require(self, provider_id: str) -> ModelProvider:
        """Return one provider by id or raise a clear error."""
        provider = self.get(provider_id)
        if provider is None:
            raise ModelProviderNotFoundError(f"unknown model provider: {provider_id}")
        return provider

    def list(self) -> list[ModelProvider]:
        """Return registered providers in stable id order."""
        return [self._providers[key] for key in sorted(self._providers)]


def default_model_provider_registry() -> ModelProviderRegistry:
    """Return built-in provider metadata for local fixture workflows."""
    return ModelProviderRegistry(
        [
            ModelProvider.model_validate(
                {
                    "id": "provider_fixture_local",
                    "name": "Fixture Local Provider",
                    "provider": "fixture",
                    "modes": ["chat", "runner"],
                    "capabilities": [
                        {
                            "name": "model.chat",
                            "mode": "chat",
                            "description": "Fixture chat completion.",
                            "grant_required": True,
                        },
                        {
                            "name": "runner.execute",
                            "mode": "runner",
                            "description": "Fixture runner execution.",
                            "grant_required": True,
                        },
                    ],
                    "trust_boundary": "local",
                    "config_refs": ["CRAIK_PROVIDER_FIXTURE_MODE"],
                    "secret_ref_names": ["CRAIK_PROVIDER_FIXTURE_TOKEN"],
                    "budget_ref": "budget_fixture_monthly",
                    "quota_ref": "quota_fixture_daily",
                    "runtime_path": "craik.runtime.fixture_provider",
                    "metadata": {"notes": "Fixture provider metadata only."},
                    "docs": ["docs/reference/model-providers.md"],
                    "created_at": datetime.now(UTC),
                }
            )
        ]
    )


def provider_selection_payload(
    provider: ModelProvider,
    *,
    mode: str,
    policy_envelope_id: str | None = None,
    receipt_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Return a redacted provider selection payload for operator output."""
    if mode not in provider.modes:
        supported = ", ".join(provider.modes)
        raise ValueError(
            f"provider {provider.id} does not support mode {mode!r}; supported: {supported}"
        )
    return {
        "provider_id": provider.id,
        "provider": provider.provider,
        "name": provider.name,
        "mode": mode,
        "trust_boundary": provider.trust_boundary,
        "runtime_path": provider.runtime_path,
        "config_refs": provider.config_refs,
        "secret_ref_names": provider.secret_ref_names,
        "budget_ref": provider.budget_ref,
        "quota_ref": provider.quota_ref,
        "policy_envelope_id": policy_envelope_id,
        "receipt_ids": receipt_ids or [],
        "redacted": True,
    }
