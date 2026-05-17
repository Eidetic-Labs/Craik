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
- budget and quota reference names;
- optional runtime path;
- docs links.

## Secret Boundary

Provider metadata must not contain secret-like keys such as API keys, tokens,
passwords, credentials, or secrets. Public provider records may name secret
references, but they must not include secret values.

Use `config_refs` for non-secret configuration names and `secret_ref_names` for
external secret handles.

Use `budget_ref` and `quota_ref` for non-secret budget and quota handles. Do not
store billing credentials, account tokens, or provider console secrets in model
provider records.

## Registry

`craik.runtime.model_providers.ModelProviderRegistry` provides in-memory
registration and lookup by stable provider id. Duplicate provider ids are
rejected, and missing providers raise a clear lookup error.

The registry is metadata-only. It does not call providers, load credentials, or
grant execution authority by itself.

The default registry includes three built-in providers:

- `provider_fixture_local` for deterministic local workflows;
- `provider_openai` for OpenAI Responses API-compatible MVP execution;
- `provider_anthropic` for Anthropic Messages API-compatible MVP execution.

OpenAI and Anthropic records use third-party trust boundaries, external secret
references, budget and quota references, and runtime adapter paths under
`craik.runtime.provider_runtime`. Their default model metadata is non-secret and
may be overridden by the named configuration references before live use.

## Provider Runtime

`craik.runtime.provider_runtime` defines the provider-neutral request, result,
adapter, retry decision, and receipt helpers used by the MVP provider path.

The OpenAI adapter builds Responses API-style payloads with:

- system messages mapped to developer messages;
- `stream` passthrough;
- function tools with strict JSON schemas;
- structured output through `text.format`;
- normalized usage metadata and tool calls.

The Anthropic adapter builds Messages API-style payloads with:

- top-level system instructions;
- user and assistant messages in the message list;
- `stream` passthrough;
- client tool declarations with `input_schema`;
- structured output as a forced client tool;
- normalized usage metadata and tool calls.

Both adapters classify retryable API conditions and gate live access behind an
explicit `live_enabled=true` runtime setting. Deterministic tests use fixtures
and normalized payloads; they do not contact live providers.

## Provider-Backed Runner Path

`craik.runtime.provider_runner` connects the provider runtime to the governed
single-agent loop. The MVP path:

- builds or loads the task case file;
- compiles a provider-runner prompt from the case file and policy envelope;
- executes the loop through `provider_openai` or `provider_anthropic`;
- records provider receipts for every model step;
- preserves side-effect receipts from the loop;
- persists normalized run outputs;
- creates a durable handoff for completed, blocked, failed, and interrupted
  outcomes.

The default provider-backed path remains deterministic. It certifies the Craik
handoff, receipt, and output plumbing without contacting live APIs. Live provider
transport must be enabled explicitly by future caller configuration.

## Budget And Quota Checks

`craik.runtime.provider_budgets` evaluates non-secret provider budget status
before routing. Routing is blocked when:

- status belongs to a different provider;
- the status is explicitly blocked;
- remaining budget is zero or below;
- remaining quota is zero or below.

Allowed decisions preserve the provider id, budget ref, quota ref, and remaining
budget/quota values for later receipts.

## Official Docs Verified

Provider assumptions for the MVP runtime were checked against official provider
docs on 2026-05-17:

- OpenAI Responses API, streaming responses, structured outputs, function
  calling, and model docs.
- Anthropic Messages API, streaming messages, tool use, model overview, and rate
  limit docs.
