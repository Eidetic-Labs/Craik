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
