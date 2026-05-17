import pytest
from pydantic import ValidationError

from craik.runtime.companions.locale_i18n import (
    LocalePreference,
    TranslatableDocMetadata,
    resolve_doc_locale,
)


def test_resolve_doc_locale_uses_exact_translation() -> None:
    resolution = resolve_doc_locale(
        metadata=_metadata(
            available_locales=["en-US", "es-MX"],
            translated_paths={"es-MX": "docs/es-MX/reference/receipts.md"},
        ),
        preference=LocalePreference(
            id="project_locale",
            preferred_locale="es-MX",
        ),
    )

    assert resolution.requested_locale == "es-MX"
    assert resolution.resolved_locale == "es-MX"
    assert resolution.status == "translated"
    assert resolution.path == "docs/es-MX/reference/receipts.md"
    assert resolution.fallback_chain == ["es-MX"]
    assert resolution.policy_envelope_id == "policy_i18n"
    assert resolution.evidence_ids == ["evidence_source_doc"]


def test_resolve_doc_locale_falls_back_to_language_then_default() -> None:
    resolution = resolve_doc_locale(
        metadata=_metadata(
            available_locales=["en-US", "es"],
            translated_paths={"es": "docs/es/reference/receipts.md"},
        ),
        preference=LocalePreference(
            id="project_locale",
            preferred_locale="es-MX",
            fallback_locales=["fr-FR"],
        ),
    )

    assert resolution.resolved_locale == "es"
    assert resolution.status == "fallback"
    assert resolution.path == "docs/es/reference/receipts.md"
    assert resolution.fallback_chain == ["es-MX", "es"]


def test_resolve_doc_locale_can_use_configured_default() -> None:
    resolution = resolve_doc_locale(
        metadata=_metadata(
            available_locales=["en-US", "fr-FR"],
            translated_paths={"fr-FR": "docs/fr-FR/reference/receipts.md"},
        ),
        preference=LocalePreference(
            id="project_locale",
            preferred_locale="es-MX",
            fallback_strategy="exact_then_default",
            default_locale="fr-FR",
        ),
    )

    assert resolution.resolved_locale == "fr-FR"
    assert resolution.status == "fallback"
    assert resolution.fallback_chain == ["es-MX", "fr-FR"]


def test_resolve_doc_locale_defaults_to_source_when_translation_is_missing() -> None:
    resolution = resolve_doc_locale(
        metadata=_metadata(),
        preference=LocalePreference(
            id="project_locale",
            preferred_locale="ja-JP",
        ),
    )

    assert resolution.resolved_locale == "en-US"
    assert resolution.status == "fallback"
    assert resolution.path == "docs/reference/receipts.md"
    assert resolution.redaction_required is True


def test_locale_preference_validates_required_locale_fields() -> None:
    with pytest.raises(ValidationError, match="preferred_locale"):
        LocalePreference(
            id="project_locale",
            preferred_locale="",
        )

    with pytest.raises(ValidationError, match="formatting_locale"):
        LocalePreference(
            id="project_locale",
            preferred_locale="en-US",
            formatting_locale="",
        )


def test_translatable_doc_metadata_preserves_i18n_boundaries() -> None:
    with pytest.raises(ValidationError, match="source_locale"):
        _metadata(available_locales=["es-MX"])

    with pytest.raises(ValidationError, match="language-neutral"):
        _metadata(identifiers_language_neutral=False)

    with pytest.raises(ValidationError, match="semantics"):
        _metadata(semantics_preserved=False)

    with pytest.raises(ValidationError, match="policy_envelope_id"):
        _metadata(policy_envelope_id="")


def _metadata(**overrides: object) -> TranslatableDocMetadata:
    payload = {
        "stable_id": "reference.receipts",
        "source_path": "docs/reference/receipts.md",
        "source_locale": "en-US",
        "available_locales": ["en-US"],
        "translated_paths": {},
        "policy_envelope_id": "policy_i18n",
        "evidence_ids": ["evidence_source_doc"],
        "receipt_ids": ["receipt_i18n_review"],
    }
    payload.update(overrides)
    return TranslatableDocMetadata.model_validate(payload)
