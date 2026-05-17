# Provider Certification

Craik's MVP provider surface must support OpenAI and Anthropic through the same
certification bar. Provider metadata alone is not enough; a provider is MVP-ready
only when tests and receipts show that the runtime can safely use it in a
governed workflow.

## MVP Requirements

Each certified provider path must cover:

- chat;
- streaming;
- tool calls;
- structured output;
- usage metadata;
- retryable errors;
- redaction;
- receipts.

`ProviderCertification` records the provider family, model references,
requirements that passed, requirements that are blocked, policy envelope,
evidence, receipts, and documentation reference.

`provider_certification_decision` returns `certified` only when every MVP
requirement is supported and no requirement is blocked.

## Provider Families

The MVP provider families are:

- `openai`;
- `anthropic`.

Both providers use secret references for API credentials. Public metadata,
receipts, docs, and certification fixtures must not include raw API keys,
organization secrets, request bodies containing private task text, or provider
console credentials.

## Implementation Boundary

Before implementing live API behavior, provider-specific assumptions should be
verified against official provider documentation. Certification tests should
remain deterministic by default and use fixtures unless a live smoke profile is
explicitly enabled.

## MVP Runtime Certification

The MVP provider runtime certification is implemented as deterministic tests
against `craik.runtime.provider_runtime`. The tests certify both OpenAI and
Anthropic for:

- request payload construction for chat, streaming, tools, and structured
  output;
- response normalization for text, tool calls, structured output, response ids,
  and usage metadata;
- retry decisions for provider throttling, transient failures, and overloads;
- secret-reference-only configuration;
- redacted provider receipts;
- explicit live-access gating.

Live provider calls remain disabled unless a caller constructs an adapter with
`live_enabled=true` and supplies credentials through an external secret resolver.
Provider metadata, receipts, CLI output, docs, and test fixtures must continue to
name secret references only.

## Official Provider References

OpenAI MVP assumptions were verified against official OpenAI docs for Responses,
streaming responses, structured outputs, function calling, and models.

Anthropic MVP assumptions were verified against official Anthropic docs for
Messages, streaming messages, tool use, model names, and rate limits.
