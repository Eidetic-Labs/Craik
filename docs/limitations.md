# Limitations

Craik is preparing for a robust `0.x.0` MVP release. The repository has broad
contract, helper, CLI, and documentation coverage through the v0.13 roadmap, but
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
- Deterministic OpenAI and Anthropic provider-backed MVP runner paths.
- The Stigmem documentation reconciliation demo as the release acceptance path.

## Contract Or Helper Surfaces

- Provider execution is fixture-backed by default. Live HTTP requests require
  setting `live_enabled=true` on the `ProviderRuntimeConfig` and supplying an
  environment-variable-backed secret reference, such as `ANTHROPIC_API_KEY` or
  `OPENAI_API_KEY`. CI does not exercise the live path; tests run against
  either `FixtureTransport` or recorded cassettes.
- Runner adapters outside the MVP OpenAI and Anthropic provider paths are
  preview, fixture, or prompt-handoff oriented.
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

- Live model invocation behind explicit operator configuration.
- Bounded real tool execution behind least-privilege grants.
- Tool execution is policy-gated but does not yet run inside a sandbox. Granted
  tool calls execute in the host process; sandbox backends (`docker_sandbox`,
  `local_process`, `remote_shell`) define contracts but do not yet isolate
  execution.
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
Package version `0.1.0` marks the first explicit live provider transport path.
Roadmap milestones such as v0.13 remain implementation gates rather than
published package compatibility guarantees.
