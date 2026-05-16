"""Model provider registry helpers."""

from __future__ import annotations

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
