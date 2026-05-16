# Model Providers

`craik.model_provider` records model provider and runtime execution path
metadata for provider routing.

The contract captures:

- stable provider id;
- provider name;
- provider family;
- supported modes, such as `chat`, `completion`, `embedding`, `tool`, and
  `runner`;
- capability declarations;
- trust boundary;
- non-secret configuration references;
- secret reference names;
- optional runtime path;
- docs links.

## Secret Boundary

Provider metadata must not contain secret-like keys such as API keys, tokens,
passwords, credentials, or secrets. Public provider records may name secret
references, but they must not include secret values.

Use `config_refs` for non-secret configuration names and `secret_ref_names` for
external secret handles.

## Registry

`craik.runtime.model_providers.ModelProviderRegistry` provides in-memory
registration and lookup by stable provider id. Duplicate provider ids are
rejected, and missing providers raise a clear lookup error.

The registry is metadata-only. It does not call providers, load credentials, or
grant execution authority by itself.
