# Robust MVP Roadmap

Craik's first public release target is a robust `0.x.0` MVP, not `1.0.0`.
`1.0.0` remains a later stability signal after real-world usage, compatibility
confidence, and security soak. The MVP must still include the readiness work
that affects trust, release hygiene, documentation accuracy, provider support,
and package publication.

## MVP Definition

The MVP is complete when Craik can run one real software-delivery workflow end
to end with OpenAI and Anthropic provider support, policy-enforced side effects,
durable receipts, a useful handoff, accurate documentation, and package-release
quality gates.

The accepted proof workflow remains Stigmem documentation and state
reconciliation. It must run from a clean install, assemble a case file, use a
certified provider path, record receipts, produce a handoff, and leave memory
updates or proposals with evidence.

## Status Classes

- `end-to-end`: implemented as a user-facing workflow with persistence, docs,
  tests, and CI coverage.
- `contract/helper`: implemented as models, evaluators, formatters, or fixtures
  but not as an operational workflow.
- `docs-only`: documented as a product decision or strategy.
- `deferred`: intentionally outside the first MVP.

## Execution Checklist

### 0. Roadmap Reset And Status Truth

Tracking issue: [#298](https://github.com/Eidetic-Labs/Craik/issues/298).

- [x] Replace stale `pre-0.1.0` language in public docs.
- [x] State that the first release is `0.x.0`.
- [x] Add a surface status matrix.
- [x] Convert the post-v0.13 readiness list into MVP and post-MVP buckets.

### 1. Docusaurus Docs Platform

Tracking issue: [#299](https://github.com/Eidetic-Labs/Craik/issues/299).

- [x] Add a Docusaurus site.
- [x] Mirror Stigmem's `Learn`, `Build`, `Operate`, and `Secure` IA.
- [x] Add local search, Mermaid support, code blocks, redirects, and broken-link
  enforcement.
- [x] Add generated CLI/reference docs.
- [x] Add docs build CI and publish-ready Pages workflow.

### 2. Release And Package Foundation

Tracking issue: [#297](https://github.com/Eidetic-Labs/Craik/issues/297).

- [x] Define `0.x.0` release cadence and tag policy.
- [x] Add version consistency checks.
- [x] Add package build verification.
- [x] Add PyPI publish workflow with protected environment.
- [x] Add changelog and release note workflow.
- [x] Add security release process.

### 3. CI/CD Parity With Stigmem

Tracking issue: [#300](https://github.com/Eidetic-Labs/Craik/issues/300).

- [x] Split CI into path-filtered jobs.
- [x] Add lint, type, unit, contract, docs, security, and package jobs.
- [x] Add coverage baseline and ratchet.
- [x] Add changed-file strictness checks.
- [x] Add conformance suites.
- [x] Add nightly reliability workflow.
- [x] Upload test, docs, coverage, and conformance artifacts.

### 4. Persistent State Migrations

Tracking issue: [#303](https://github.com/Eidetic-Labs/Craik/issues/303).

- [x] Add local store schema versioning.
- [x] Add forward migrations.
- [x] Add fixture databases for previous schema versions.
- [x] Add migration compatibility tests.
- [x] Add migration failure and recovery docs.

### 5. Provider Runtime: OpenAI And Anthropic

Tracking issue: [#304](https://github.com/Eidetic-Labs/Craik/issues/304).

- [x] Add provider abstraction for chat, streaming, tool calls, structured output,
  retries, errors, and usage metadata.
- [x] Implement OpenAI provider adapter.
- [x] Implement Anthropic provider adapter.
- [x] Store API access as secret references, not raw keys.
- [x] Add provider receipts and redaction behavior.
- [x] Add certification fixtures and tests for both providers.
- [x] Verify official provider docs before implementation work that depends on
  live API behavior.

### 6. One Complete MVP Runner Path

Tracking issue: [#302](https://github.com/Eidetic-Labs/Craik/issues/302).

- [x] Connect case file assembly to prompt compilation.
- [x] Execute one provider-backed run loop.
- [x] Persist normalized runner outputs.
- [x] Create receipts for side effects and provider calls.
- [x] Produce durable handoffs on completion, block, failure, and interruption.
- [x] Add OpenAI and Anthropic parity checks for the MVP task path.

### 7. Policy-Enforced Side Effects

Tracking issue: [#301](https://github.com/Eidetic-Labs/Craik/issues/301).

- [x] Add shell execution wrapper with grants and receipts.
- [x] Add file write wrapper with immutable path protection.
- [x] Add policy-gated Stigmem write wrapper.
- [x] Add guarded GitHub writes if required by the MVP proof workflow.
- [x] Add denial receipts for blocked side effects.
- [x] Add redaction regression tests for all side-effect receipts.

### 8. Stigmem And Memory Hardening

Tracking issue: [#305](https://github.com/Eidetic-Labs/Craik/issues/305).

- [x] Load Stigmem facts into case files.
- [x] Load recent handoffs into case files.
- [x] Load local contradiction reports into case files.
- [x] Add direct granted Stigmem writes.
- [x] Keep proposals as the default unprivileged path.
- [x] Add memory hygiene workflow.
- [x] Preserve provenance and source attestation metadata.

### 9. Public/Internal Boundary And Provenance Docs

Tracking issue: [#306](https://github.com/Eidetic-Labs/Craik/issues/306).

- [x] Add public/internal boundary classifier.
- [x] Add provenance-aware documentation workflow.
- [x] Add generated doc evidence links.
- [x] Add stale documentation detection.
- [x] Add work product classification.
- [x] Add decision record suggestions.
- [x] Add CI checks preventing public docs from exposing secrets, private paths,
  or private task names.

### 10. MVP Demo And Acceptance Workflow

Tracking issue: [#308](https://github.com/Eidetic-Labs/Craik/issues/308).

- [x] Build the Stigmem docs reconciliation demo as the release acceptance path.
- [x] Support OpenAI and Anthropic provider execution for the demo.
- [x] Produce case file, receipts, handoff, memory proposal/write, and graph
  export.
- [x] Add quickstart smoke CI.
- [x] Add Docusaurus tutorial that mirrors the executable demo exactly.

### 11. Hardening And Failure Modes

Tracking issue: [#307](https://github.com/Eidetic-Labs/Craik/issues/307).

- [x] Document limits and failure modes.
- [x] Add adversarial prompt-injection tests.
- [x] Add secret leakage tests.
- [x] Add bad tool-call and policy-bypass tests.
- [x] Add timeout, retry, and budget tests.
- [x] Add contract conformance tests for persisted payloads.

### 12. Post-MVP Deferrals

Tracking issue: [#309](https://github.com/Eidetic-Labs/Craik/issues/309).

- [x] Mark full gateway daemon as post-MVP unless required by the proof workflow.
- [x] Mark full TUI/dashboard as post-MVP.
- [x] Mark additional live runner adapters as post-MVP.
- [x] Mark companion/mobile/visual surfaces as post-MVP.
- [x] Mark broad marketplace/community ecosystem as post-MVP.
- [x] Keep contract/helper docs honest for deferred surfaces.

## Eighteen Readiness Capabilities

These capabilities are addressed by the MVP roadmap rather than deferred to a
first `1.0.0` release:

1. stable core schemas;
2. persisted state migrations;
3. SemVer release process;
4. package publication;
5. security release process;
6. complete generated CLI/reference docs;
7. production-quality Stigmem integration;
8. documented limits and failure modes;
9. runnable demo;
10. community contribution path;
11. at least one complete runner adapter supported end to end;
12. policy tests in CI;
13. public/internal boundary classifier;
14. provenance-aware documentation workflow;
15. memory hygiene workflow;
16. work product classification;
17. decision record suggestions;
18. learning without self-trust.

## MVP Acceptance Criteria

- [ ] A clean install can run the accepted demo.
- [ ] OpenAI and Anthropic provider paths both pass certification tests.
- [ ] Side effects are policy-gated and receipt-backed.
- [ ] Redaction is applied before persistence and docs publication.
- [ ] Local store migrations are tested against fixture states.
- [ ] Docusaurus docs build with no broken links.
- [ ] CI includes lint, type, unit, docs, package, security, and conformance
  gates.
- [ ] Package artifacts build and can be published through a protected workflow.
- [ ] Known limitations are accurate and visible.
