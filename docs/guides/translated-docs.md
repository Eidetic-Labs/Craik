# Translated Documentation Strategy

Craik documentation starts from English source-of-truth pages and uses
translation metadata to expose localized docs without changing runtime
contracts. Translations are presentation surfaces; they do not redefine policy,
evidence, receipt, redaction, schema, or identifier semantics.

## Source Of Truth

The canonical documentation lives under `docs/` and is authored as the source
locale for each page. Translated pages may live in locale-specific paths when
they are reviewed and linked through metadata described in
[Locale I18n Framework](../reference/locale-i18n-framework.md).

Source-of-truth pages define:

- stable language-neutral document ids;
- canonical links to contracts and guides;
- policy, evidence, receipt, and redaction semantics;
- public boundary requirements;
- the fallback path used when a translation is unavailable.

Translations must preserve those semantics. If a translation cannot preserve
the meaning of a policy rule, schema field, receipt status, or redaction
requirement, the translated page should remain deferred and link back to the
source page.

## Translation Metadata

Each translatable page should have metadata that records:

- stable document id;
- source path and source locale;
- available locales and translated paths;
- policy envelope id governing translation review;
- evidence references for source material and review;
- receipt references for translation checks;
- redaction requirement;
- confirmation that runtime identifiers remain language-neutral.

This metadata is represented by `TranslatableDocMetadata` and resolved through
`resolve_doc_locale`. The resolution result records the requested locale,
resolved locale, fallback chain, path, and policy/evidence/receipt context.

## Fallback Links

Translated docs should include a path back to the source page when a locale is
incomplete, stale, community-maintained, or deferred. Runtime link resolution
should prefer:

1. exact locale;
2. language-only locale when configured;
3. configured fallback locales;
4. source locale.

Fallback links must point to public docs pages only. They must not expose local
filesystem paths, private planning labels, credentials, or private task names.

## Review Expectations

Translation review should verify:

- public boundary language is preserved;
- redaction markers and secret references are not translated into secret values;
- schema names, ids, receipt ids, policy ids, memory entities, and task ids are
  unchanged;
- code blocks and CLI commands remain technically valid;
- links resolve through docs tests or documented deferred status;
- any machine-generated translation has human or policy review before being
  marked supported.

Review receipts should record the source page, target locale, review evidence,
reviewer or automation id, and whether policy/evidence/receipt/redaction
semantics were preserved.

## Deferred And Community-Maintained Translations

A locale may be marked deferred when there is no reviewer, when terminology is
not settled, or when source docs are changing too quickly. Deferred translations
should use fallback links rather than stale translated prose.

Community-maintained translations are acceptable when they follow the same
metadata, review, public boundary, and receipt expectations as core
translations. Community status should be visible in the translation metadata or
review receipt, and source docs remain authoritative when conflicts appear.

## Limits

Translated docs must not:

- translate runtime identifiers or schema names;
- weaken policy, approval, capability grant, receipt, evidence, or redaction
  requirements;
- introduce examples with real credentials, private paths, or private task
  names;
- imply unsupported locale-specific behavior exists in the runtime;
- bypass docs link validation except through explicitly documented deferred
  status.
