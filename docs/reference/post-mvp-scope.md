# Post-MVP Scope

Craik's first robust MVP is a `0.x.0` release, not a `1.0.0` compatibility
promise. MVP scope is limited to the accepted documentation reconciliation
workflow, deterministic OpenAI and Anthropic provider paths, local state,
policy-gated side effects, memory proposals, receipts, handoffs, work graphs,
package release workflows, and Docusaurus documentation.

The surfaces below are intentionally post-MVP unless a later roadmap gate makes
them part of a specific proof workflow.

## Gateway Daemon

Gateway contracts and deterministic lifecycle helpers may exist before MVP, but
a full always-on daemon, inbound messaging loop, webhook dispatcher, scheduler,
and externally reachable service are post-MVP. They must not be documented as
operational support until they have policy checks, receipts, supervision,
security review, and CI coverage.

## Operator UI

Formatter contracts and read-only operator view helpers can support local
inspection. A complete TUI, web dashboard, mutation-capable console, and hosted
operator service are post-MVP.

## Additional Live Runners

OpenAI and Anthropic are the MVP provider targets. Fixture and prompt-handoff
adapters can remain documented for local testing and preview workflows, but
additional live runner adapters are post-MVP until they meet the same
certification, budget, retry, redaction, receipt, and side-effect boundaries.

## Companion And Visual Surfaces

Desktop companion, mobile companion, voice, browser, visual workspace,
multimodal, and adjacent runtime surfaces are posture and contract work before
MVP. Product applications, always-on actions, remote action queues, credential
storage, and direct mutation through those surfaces are post-MVP.

## Marketplace And Community Ecosystem

Community skill, plugin, marketplace, index, probation, and reference
integration docs describe future contribution mechanics. They do not imply a
supported public marketplace, automatic trust, or runtime authority in the MVP.

## Documentation Rule

Docs for deferred surfaces should use one of these postures:

- `implemented`: available in the MVP path with tests and CI coverage;
- `preview`: contract, helper, fixture, or deterministic local workflow only;
- `post-MVP`: intentionally outside the first robust MVP.

Do not describe a deferred surface as operational unless the same page names the
proof workflow, required policy boundary, receipts, and validation command.
