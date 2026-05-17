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

## Contract Or Helper Surfaces

- OpenAI and Anthropic provider execution are not yet implemented. The MVP must
  add provider adapters, certification fixtures, usage metadata, retries,
  streaming/tool-call boundaries, and receipts.
- Runner adapters are currently preview and fixture-oriented. They do not yet
  provide a complete provider-backed MVP workflow.
- Execution backends evaluate boundaries and policy requirements, but they do
  not execute shell commands, start containers, open remote shells, or drive
  browsers.
- Gateway, webhook, messaging, channel, and scheduled automation surfaces are
  contracts/helpers. They do not yet run a production daemon or dispatch loop.
- Operator experience is formatter and view-contract level. A full TUI or
  dashboard is post-MVP unless explicitly pulled into the proof workflow.
- Companion, mobile, visual, and multimodal surfaces are posture decisions and
  adapter contracts, not shipped product applications.

## Known MVP Gaps

- Docusaurus documentation site with Learn / Build / Operate / Secure
  information architecture.
- Generated CLI/reference docs.
- Release, package publication, and security release workflows.
- Persistent local-store migrations and compatibility fixtures.
- CI/CD depth comparable to Stigmem: path-filtered jobs, coverage ratchets,
  docs builds, conformance tests, nightly reliability, and artifact uploads.
- Public/internal boundary classifier and provenance-aware documentation
  workflow.
- Memory hygiene workflow, work product classification, and decision record
  suggestions.
- One complete provider-backed workflow using OpenAI and Anthropic.

## Write Authority

Craik does not grant ambient write authority. Direct durable memory writes,
GitHub writes, shell commands, file writes, and external side effects must be
policy-gated, redacted, and receipt-backed before they are considered MVP-ready.
Local memory proposals remain the default unprivileged path.

## Release Posture

The first release target is `0.x.0`. The release must be honest about limits and
strong enough for a credible MVP, but it is not a `1.0.0` stability guarantee.
