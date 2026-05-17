# ADR 0001: Record MVP Runner Scope

## Status

Accepted

## Context

Craik's public framing must match the shipped artifact. The MVP already has
case-file assembly, policy envelopes, prompt compilation, receipts, handoffs,
work graphs, local memory proposals, Stigmem-compatible reads, and deterministic
OpenAI- and Anthropic-shaped provider runner paths. It does not yet perform live
model calls, arbitrary tool execution, file edits, or remote Stigmem writes
without an explicit grant flow.

## Decision

The MVP runner path is a deterministic provider-backed certification path by
default. It validates the contracts and policy boundaries for OpenAI and
Anthropic provider families without making live model calls in tests or demos.

Live model invocation and real side effects will be added behind explicit
configuration, least-privilege grants, redacted receipts, and release-gate
coverage. Documentation must describe preview Codex, Claude, and Gemini adapters
as prompt-handoff or fixture adapters until those adapters invoke real runners.

## Consequences

- README and MVP docs lead with the true current surface instead of promising a
  fully autonomous agent runtime.
- `craik run execute` is the operator command for the deterministic MVP runner
  workflow.
- Policy tests include a provider-runner grant boundary check instead of a
  placeholder.
- Future work should prioritize live invocation, bounded tool execution, remote
  Stigmem write promotion, and package cleanup before expanding the surface area.
