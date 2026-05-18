from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from craik.contracts.models import ModelProvider
from craik.runtime.providers.model_providers import (
    ModelProviderRegistry,
    ModelProviderRegistryError,
)
from craik.runtime.providers.provider_config import (
    OPENAI_OFFICIAL_DOCS,
    ProviderRuntimeConfig,
)
from craik.runtime.providers.provider_runtime import ProviderRuntimeError
from craik.runtime.providers.provider_runtime_support import _provider_base_url
from craik.runtime.providers.provider_url_safety import (
    ProviderURLSafetyError,
    assert_safe_provider_url,
)


def test_provider_base_url_allows_public_https() -> None:
    assert_safe_provider_url("https://api.openai.com", allow_local=False)


def test_provider_base_url_rejects_public_http_without_local_opt_in() -> None:
    with pytest.raises(ProviderURLSafetyError, match="HTTPS"):
        assert_safe_provider_url("http://api.openai.com", allow_local=False)


def test_provider_base_url_rejects_link_local_metadata_address() -> None:
    with pytest.raises(ProviderURLSafetyError, match="private network"):
        assert_safe_provider_url("http://169.254.169.254/latest/meta-data/", allow_local=True)


def test_provider_base_url_allows_local_loopback_when_explicit() -> None:
    assert_safe_provider_url("http://localhost:11434/v1", allow_local=True)


def test_provider_base_url_rejects_private_network_address() -> None:
    with pytest.raises(ProviderURLSafetyError, match="private network"):
        assert_safe_provider_url("http://10.0.0.5/v1", allow_local=True)


def test_provider_base_url_defers_dns_names_to_runtime_resolution() -> None:
    assert_safe_provider_url("https://internal.corp.example.com", allow_local=False)


def test_provider_registry_validates_configured_base_url() -> None:
    with pytest.raises(ModelProviderRegistryError, match="private network"):
        ModelProviderRegistry(
            [
                _provider(
                    provider_id="provider_openai",
                    base_url="https://127.0.0.1/v1",
                )
            ]
        )


def test_provider_runtime_config_validates_base_url() -> None:
    with pytest.raises(ValidationError, match="private network"):
        ProviderRuntimeConfig(
            provider_id="provider_openai",
            provider_family="openai",
            model="gpt-5.2",
            secret_ref_name="OPENAI_API_KEY",
            base_url="https://127.0.0.1/v1",
            docs_refs=list(OPENAI_OFFICIAL_DOCS),
        )


def test_provider_runtime_config_allows_explicit_local_base_url() -> None:
    config = ProviderRuntimeConfig(
        provider_id="provider_local_openai_compatible",
        provider_family="chat_completions",
        model="llama3.2",
        secret_ref_name="",
        base_url="http://localhost:11434/v1",
        allow_local_base_url=True,
        docs_refs=list(OPENAI_OFFICIAL_DOCS),
    )

    assert config.base_url == "http://localhost:11434/v1"


def test_provider_base_url_runtime_double_check_rejects_unsafe_metadata() -> None:
    provider = _provider(
        provider_id="provider_openai",
        base_url="http://169.254.169.254/latest/meta-data/",
    )

    with pytest.raises(ProviderRuntimeError, match="HTTPS"):
        _provider_base_url(provider)


def _provider(
    *,
    provider_id: str,
    base_url: str,
    allow_local_base_url: bool = False,
) -> ModelProvider:
    return ModelProvider.model_validate(
        {
            "id": provider_id,
            "name": "Test Provider",
            "provider": "openai",
            "modes": ["chat"],
            "capabilities": [
                {
                    "name": "model.chat",
                    "mode": "chat",
                    "description": "Provider chat request execution.",
                    "grant_required": True,
                }
            ],
            "trust_boundary": "third-party",
            "secret_ref_names": ["OPENAI_API_KEY"],
            "metadata": {
                "base_url": base_url,
                "allow_local_base_url": allow_local_base_url,
            },
            "docs": ["docs/reference/model-providers.md"],
            "created_at": datetime.now(UTC),
        }
    )
