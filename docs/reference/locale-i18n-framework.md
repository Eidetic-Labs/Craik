# Locale I18n Framework

Craik locale support keeps runtime identifiers stable and language-neutral while
allowing docs and operator-facing text to resolve through locale preferences and
fallbacks. Translation must not change policy, evidence, receipt, or redaction
semantics.

## Locale Preferences

`LocalePreference` records:

- the preferred locale;
- fallback locales;
- the default locale;
- fallback strategy;
- optional formatting locale.

The fallback strategy controls locale resolution:

- `exact_then_language`: try the full locale, then the language subtag, then
  configured fallbacks and the default locale;
- `exact_then_default`: try the full locale, then configured fallbacks and the
  default locale;
- `default_only`: skip user fallbacks and use the default locale after the
  preferred locale.

## Translatable Docs

`TranslatableDocMetadata` records a stable language-neutral id, source path,
source locale, available locales, translated paths, policy envelope, evidence,
receipts, and redaction requirements.

Runtime identifiers, schema names, receipt ids, policy envelope ids, evidence
ids, memory entities, and task ids remain language-neutral. Translation may
change operator-facing prose, but it must not translate these identifiers or
alter their meaning.

## Resolution

`resolve_doc_locale` returns a `LocaleResolution` with:

- requested locale;
- resolved locale;
- status: `source`, `translated`, `fallback`, or `missing`;
- resolved path;
- fallback chain;
- policy, evidence, receipt, and redaction metadata.

When a translation is unavailable, Craik falls back to the configured locale
chain and ultimately to the source document. Public docs and translated exports
must continue to avoid credentials, private local paths, and private task names.

## Boundaries

Locale support must preserve:

- policy decisions and policy envelope references;
- evidence links and receipt links;
- redaction markers and secret references;
- stable runtime identifiers;
- formatting boundaries for dates, numbers, and locale-specific display text.

Translation review receipts should record the source document, translated
locale, reviewer or automation evidence, and confirmation that policy and
redaction semantics were preserved.
