# Stigmem Integration

Craik should use Stigmem as its reference memory and truth substrate.

## Boundary

Stigmem owns:

- facts,
- provenance,
- scopes,
- trust metadata,
- contradiction tracking,
- federation,
- auth,
- and memory plugin hooks.

Craik owns:

- task orchestration,
- project case files,
- agent role assignment,
- capability grants,
- receipts,
- handoffs,
- work graph state,
- and operator workflows.

## Memory Store Interface

Craik should define a memory store interface based on capabilities.

Required base capabilities:

- read facts,
- propose facts,
- write facts,
- search facts,
- list facts by entity,
- attach provenance,
- and record handoff references.

Advanced capabilities:

- contradiction detection,
- trust tiers,
- scoped visibility,
- memory diff,
- fact expiration or stale-risk markers,
- and federation.

## Stigmem Fact Usage

Craik should use Stigmem facts to assemble case files.

Relevant fact types:

- repo current state,
- branch and PR status,
- docs policy,
- ADR policy,
- implementation decisions,
- known gaps,
- stale-risk docs,
- agent handoffs,
- capability constraints,
- and project-specific conventions.

## Stigmem Fact Writes

Craik should write facts when agents learn reusable project state.

Examples:

- a doc policy that future agents must respect,
- a recurring validation command,
- an implementation constraint,
- a repository convention,
- a stale documentation warning,
- a completed migration status,
- or a contradiction that needs resolution.

## Handoff Storage

Craik should store handoffs as structured artifacts and write summary facts to Stigmem.

The full handoff may live in Craik storage or the repository. Stigmem should receive enough metadata for discovery:

- task id,
- repository,
- branch,
- agent identity,
- summary,
- changed artifacts,
- facts learned,
- unresolved questions,
- and handoff URI.

## Local Development

Craik should support a local memory backend for development and tests.

This should not become an alternate product thesis. The local backend exists to lower setup friction and make tests deterministic. Stigmem remains the production-grade reference backend.
