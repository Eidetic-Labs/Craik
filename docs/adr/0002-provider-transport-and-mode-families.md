# 0002 Provider Transport And Mode Families

## Context

Craik needs one provider path that can run fixtures, local OpenAI-compatible
servers, and hosted OpenAI and Anthropic APIs. The OpenAI Responses API,
Anthropic Messages API, and Chat Completions-compatible servers are related but
not interchangeable wire formats. Treating them as one adapter would hide tool,
streaming, usage, and retry differences.

## Decision

Craik separates provider families from transport. Provider adapters own payload
construction, streaming normalization, error classification, and result
normalization. Transports own delivery and chunk parsing. `FixtureTransport`
keeps deterministic tests offline, while `HTTPTransport` uses stdlib urllib for
live JSON and Server-Sent Events requests.

OpenAI Responses, Anthropic Messages, and Chat Completions are distinct provider
families. Chat Completions covers OpenAI-compatible local and hosted servers such
as Ollama, vLLM, LM Studio, and OpenRouter-shaped endpoints.

## Consequences

Provider tests can exercise adapters without network access, and live transport
hardening can evolve without rewriting provider-specific schemas. The cost is a
small amount of family-specific normalization code and certification coverage for
each supported family.

## Alternatives Considered

A single generic HTTP provider was rejected because it would push schema
branches into callers and receipts. Adding SDK dependencies was rejected for the
MVP because stdlib HTTP keeps package release and CI behavior simpler.

## Retraction

No retraction is active. Retract this ADR if Craik moves provider execution into
an external provider gateway with its own typed transport contract.
