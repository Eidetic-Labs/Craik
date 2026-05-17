# Redaction

Craik uses a central runtime redaction utility before persistence boundaries.

Module:

```text
craik.runtime.policy.redaction
```

The legacy `craik.runtime.redaction` import remains available for compatibility.

Primary APIs:

- `redact(value, config=None)`
- `contains_unredacted_secret(value, config=None)`

## Default Coverage

The default redactor covers:

- bearer tokens,
- API key, token, password, and secret assignment shapes,
- common token prefixes,
- auth URLs with embedded credentials,
- structured keys containing secret-like names.

## Structured Payloads

Redaction applies recursively to:

- dictionaries,
- lists,
- tuples,
- strings.

It preserves non-secret shape so debugging context remains useful. For example, object keys, status fields, request ids, and non-secret summaries remain intact.

## Configurable Patterns

Callers may provide custom regex patterns through `RedactionConfig`.

Custom patterns are additive when the caller includes the default patterns and additional project-specific patterns in the config.

## Persistence Boundaries

Craik treats redaction failures as security bugs. Payloads should be redacted before they are written to:

- logs,
- receipts,
- handoffs,
- case files,
- errors,
- memory proposals,
- work graph events.

The local SQLite store rejects payloads that still appear to contain unredacted secret material.
