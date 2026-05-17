# ADR 0006: Package And Runtime Layout

## Context

Craik started with broad runtime and contract modules because early milestones
were contract-heavy and issue-driven. That made discovery easy at first, but it
created god files and a flat runtime namespace that hid ownership boundaries.
The runtime now contains providers, memory, policy, work execution, companions,
channels, voice, sandboxing, and project workflows with different change rates
and risk profiles.

## Decision

Craik keeps `craik.contracts.models` and common `craik.runtime.*` imports as
compatibility surfaces, but implementation files are grouped by concern. Runtime
modules live under packages such as `runtime.providers`, `runtime.memory`,
`runtime.policy`, `runtime.work`, `runtime.runners`, `runtime.channels`,
`runtime.sandbox`, and companion packages. The root runtime package maintains
lazy legacy module aliases for moved public modules.

No runtime package should grow beyond 15 sibling Python modules without a new
layout decision or a deeper package split.

## Consequences

This makes ownership and review scope clearer while preserving existing imports.
It also adds a compatibility layer that must be tested whenever modules move.
New work should choose the package that matches the runtime concern rather than
creating one module per issue at the root.

## Alternatives Considered

Leaving compatibility shim files at the runtime root was rejected because it
would preserve the flat sibling-module problem. Updating every caller and
breaking legacy imports was rejected because Craik's public import surface is
already used by tests, docs, and downstream automation.

## Retraction

No retraction is active. Retract this ADR if Craik adopts a generated API layer
or a plugin loader that replaces direct runtime package imports.
