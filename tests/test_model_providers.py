from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.contracts.models import ModelProvider
from craik.contracts.registry import schema_model
from craik.runtime.model_providers import (
    DuplicateModelProviderError,
    ModelProviderNotFoundError,
    ModelProviderRegistry,
)

NOW = datetime(2026, 5, 16, 19, 40, tzinfo=UTC)


def _provider(**overrides: object) -> ModelProvider:
    payload: dict[str, object] = {
        "schema": "craik.model_provider",
        "version": "0.1.0",
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
        "runtime_path": "craik.runtime.fixture_provider",
        "metadata": {"notes": "Fixture provider metadata only."},
        "docs": ["docs/reference/model-providers.md"],
        "created_at": NOW,
    }
    payload.update(overrides)
    return ModelProvider.model_validate(payload)


def test_model_provider_registers_schema() -> None:
    assert schema_model("craik.model_provider") is ModelProvider


def test_model_provider_separates_config_and_secret_refs() -> None:
    provider = _provider()

    assert provider.config_refs == ["CRAIK_PROVIDER_FIXTURE_MODE"]
    assert provider.secret_ref_names == ["CRAIK_PROVIDER_FIXTURE_TOKEN"]
    assert "TOKEN" not in provider.metadata


def test_model_provider_rejects_secret_like_metadata() -> None:
    with pytest.raises(ValidationError, match="secret-like"):
        _provider(metadata={"api_key": "not-allowed"})


def test_model_provider_rejects_undeclared_capability_mode() -> None:
    with pytest.raises(ValidationError, match="undeclared modes"):
        _provider(
            modes=["chat"],
            capabilities=[
                {
                    "name": "runner.execute",
                    "mode": "runner",
                    "description": "Runner execution.",
                    "grant_required": True,
                }
            ],
        )


def test_model_provider_registry_registers_and_lists_by_id() -> None:
    provider_b = _provider(id="provider_b", name="Provider B")
    provider_a = _provider(id="provider_a", name="Provider A")
    registry = ModelProviderRegistry([provider_b, provider_a])

    assert registry.get("provider_a") == provider_a
    assert registry.require("provider_b") == provider_b
    assert [provider.id for provider in registry.list()] == ["provider_a", "provider_b"]


def test_model_provider_registry_rejects_duplicate_ids() -> None:
    provider = _provider()
    registry = ModelProviderRegistry([provider])

    with pytest.raises(DuplicateModelProviderError):
        registry.register(provider)


def test_model_provider_registry_requires_known_provider() -> None:
    registry = ModelProviderRegistry()

    with pytest.raises(ModelProviderNotFoundError, match="unknown model provider"):
        registry.require("missing")
