"""Locale and internationalization framework contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel

LocaleFallbackStrategy = Literal["exact_then_language", "exact_then_default", "default_only"]
TranslationStatus = Literal["source", "translated", "fallback", "missing"]


class LocalePreference(CraikModel):
    """Preferred locale set for a user, project, or public docs surface."""

    id: str
    preferred_locale: str
    fallback_locales: list[str] = Field(default_factory=list)
    default_locale: str = "en-US"
    fallback_strategy: LocaleFallbackStrategy = "exact_then_language"
    formatting_locale: str | None = None

    @model_validator(mode="after")
    def validate_locale_preference(self) -> LocalePreference:
        """Keep locale preferences stable and explicit."""
        if not self.preferred_locale:
            raise ValueError("locale preferences require preferred_locale")
        if not self.default_locale:
            raise ValueError("locale preferences require default_locale")
        if self.formatting_locale == "":
            raise ValueError("formatting_locale cannot be empty")
        return self


class TranslatableDocMetadata(CraikModel):
    """Metadata for a source or translated document."""

    stable_id: str
    source_path: str
    source_locale: str = "en-US"
    available_locales: list[str] = Field(default_factory=lambda: ["en-US"])
    translated_paths: dict[str, str] = Field(default_factory=dict)
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(default_factory=list)
    redaction_required: bool = True
    identifiers_language_neutral: bool = True
    semantics_preserved: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_metadata(self) -> TranslatableDocMetadata:
        """Keep translated docs policy-bound and language-neutral."""
        if not self.stable_id:
            raise ValueError("translatable docs require stable_id")
        if not self.policy_envelope_id:
            raise ValueError("translatable docs require policy_envelope_id")
        if self.source_locale not in self.available_locales:
            raise ValueError("available_locales must include source_locale")
        if not self.identifiers_language_neutral:
            raise ValueError("runtime identifiers must remain language-neutral")
        if not self.semantics_preserved:
            raise ValueError("policy, evidence, receipt, and redaction semantics must be preserved")
        return self


class LocaleResolution(CraikModel):
    """Resolved locale and document path for a translatable surface."""

    requested_locale: str
    resolved_locale: str
    status: TranslationStatus
    path: str
    fallback_chain: list[str] = Field(default_factory=list)
    stable_id: str
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(default_factory=list)
    redaction_required: bool = True


def resolve_doc_locale(
    *,
    metadata: TranslatableDocMetadata,
    preference: LocalePreference,
) -> LocaleResolution:
    """Resolve a document locale using exact, language, and default fallbacks."""
    candidates = _candidate_locales(preference)
    fallback_chain: list[str] = []
    for candidate in candidates:
        fallback_chain.append(candidate)
        if candidate in metadata.translated_paths:
            return _resolution(
                metadata=metadata,
                preference=preference,
                resolved_locale=candidate,
                status="source" if candidate == metadata.source_locale else "translated",
                path=metadata.translated_paths[candidate],
                fallback_chain=fallback_chain,
            )
        if candidate == metadata.source_locale:
            return _resolution(
                metadata=metadata,
                preference=preference,
                resolved_locale=metadata.source_locale,
                status="source",
                path=metadata.source_path,
                fallback_chain=fallback_chain,
            )

    return _resolution(
        metadata=metadata,
        preference=preference,
        resolved_locale=metadata.source_locale,
        status="missing" if metadata.source_locale not in fallback_chain else "fallback",
        path=metadata.source_path,
        fallback_chain=fallback_chain + [metadata.source_locale],
    )


def _candidate_locales(preference: LocalePreference) -> list[str]:
    candidates = [preference.preferred_locale]
    if preference.fallback_strategy == "exact_then_language":
        language = preference.preferred_locale.split("-", maxsplit=1)[0]
        if language and language != preference.preferred_locale:
            candidates.append(language)
    if preference.fallback_strategy != "default_only":
        candidates.extend(preference.fallback_locales)
    candidates.append(preference.default_locale)

    deduped: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in deduped:
            deduped.append(candidate)
    return deduped


def _resolution(
    *,
    metadata: TranslatableDocMetadata,
    preference: LocalePreference,
    resolved_locale: str,
    status: TranslationStatus,
    path: str,
    fallback_chain: list[str],
) -> LocaleResolution:
    if resolved_locale != preference.preferred_locale and status in {"source", "translated"}:
        status = "fallback"
    return LocaleResolution(
        requested_locale=preference.preferred_locale,
        resolved_locale=resolved_locale,
        status=status,
        path=path,
        fallback_chain=fallback_chain,
        stable_id=metadata.stable_id,
        policy_envelope_id=metadata.policy_envelope_id,
        evidence_ids=metadata.evidence_ids,
        receipt_ids=metadata.receipt_ids,
        redaction_required=metadata.redaction_required,
    )
