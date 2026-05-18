# Limitations

Craik is preparing for a robust `0.x.0` MVP release. The repository has broad
contract, helper, CLI, and documentation coverage through the v0.12 roadmap, but
several surfaces are not yet end-to-end production workflows.

## Current End-To-End Surfaces

- Local home and store initialization.
- Project registration and task creation.
- Case-file assembly from local repository state and optional read-only GitHub
  context.
- Local receipt, handoff, memory proposal, contradiction, and work graph
  inspection.
- Policy profile generation, capability grant checks, and policy regression
  tests.
- Stigmem compatibility detection and policy-gated direct fact write helpers.
- Deterministic fixture loop and runner preview contracts.
- Fixture-backed and live opt-in OpenAI Responses, Anthropic Messages, and
  OpenAI-compatible Chat Completions provider paths.
- OIDC operator login with device-code and loopback+PKCE flows.
- Pluggable credential sources: env-var API keys, local-CLI OAuth fallback,
  vendor-CLI bridges, external secret references, markers, and Stigmem-backed
  credential references.
- Credential pool with failover and per-profile health tracking.
- Operator and credential identity on provider receipts.
- Policy-bound operators and credentials.
- Approval-gated first credential use.
- The Stigmem documentation reconciliation demo as the release acceptance path.

## Contract Or Helper Surfaces

- Provider execution is fixture-backed by default. Live HTTP requests require
  setting `live_enabled=true` on the `ProviderRuntimeConfig` and resolving a
  provider credential through a typed auth profile, credential pool, or legacy
  secret reference. CI does not exercise paid live providers; tests run against
  `FixtureTransport`, recorded cassettes, or local stub servers.
- Runner adapters outside governed provider-backed paths remain preview,
  fixture, or prompt-handoff oriented.
- Execution backends evaluate boundaries and policy requirements, but they do
  not execute shell commands, start containers, open remote shells, or drive
  browsers.
- Gateway, webhook, messaging, channel, and scheduled automation surfaces are
  contracts/helpers. They do not yet run a production daemon or dispatch loop.
- Operator experience is formatter and view-contract level. A full TUI or
  dashboard is post-MVP unless explicitly pulled into the proof workflow.
- Companion, mobile, visual, and multimodal surfaces are posture decisions and
  adapter contracts, not shipped product applications.
- Marketplace and broad community ecosystem docs describe future contribution
  mechanics, not MVP operational support.

## Known MVP Gaps

- Resumable runs across process crashes are scheduled for v0.2.0.
- Real sandbox tool execution for one backend is scheduled for v0.2.0. Tool
  execution is policy-gated today but does not yet run inside an isolating
  sandbox boundary.
- Provider budget enforcement at the call site is scheduled for v0.2.0.
- Schema migration framework for persisted state is scheduled for v0.2.0.
- Multi-agent runtime behavior, including handoff consumption, role-based
  dispatch, and debate, is scheduled for v0.3.0.
- Runtime instruction distillation pipeline is scheduled for v0.4.0.
- Operator UI / TUI is scheduled for v0.7.0.
- Always-on gateway daemon and channel adapters are scheduled for v0.8.0.
- MCP client/server integration is scheduled for v0.9.0.
- Remote Stigmem write promotion after proposal review.
- God-file cleanup and runtime sub-packaging before the MVP freeze.
- ADR-backed design decisions for runner scope, release posture, and package
  boundaries.
- Nightly reliability and artifact depth beyond the current PR gates.
- Full post-MVP surfaces tracked in [Post-MVP Scope](reference/post-mvp-scope.md).

## Write Authority

Craik does not grant ambient write authority. Direct durable memory writes,
GitHub writes, shell commands, file writes, and external side effects must be
policy-gated, redacted, and receipt-backed before they are considered MVP-ready.
Local memory proposals remain the default unprivileged path.

## Release Posture

The first release target is `0.x.0`. The release must be honest about limits and
strong enough for a credible MVP, but it is not a `1.0.0` stability guarantee.
Package version `0.1.0` marks the first governed agent-runtime substrate with
live opt-in providers, typed credentials, and operator identity. Roadmap
milestones such as v0.12 remain implementation gates rather than published
package compatibility guarantees.
