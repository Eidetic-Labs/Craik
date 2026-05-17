# Community Plugins

Community plugins package executable or callable extensions for Craik. Treat
them as untrusted until their descriptor, provenance, review state, grants, and
receipts have been inspected.

Broad plugin marketplace and community ecosystem workflows are post-MVP scope.
This guide describes safe metadata and review boundaries; it does not imply a
supported public marketplace or runtime authority. See
[Post-MVP Scope](../reference/post-mvp-scope.md).

## Authoring

A community plugin should include:

- a governed plugin descriptor;
- versioned entrypoints;
- declared capability needs;
- compatibility metadata;
- docs and security notes;
- provenance for copied, generated, or external material;
- examples or fixtures that can be checked locally.

Use [`craik.plugin_descriptor`](../reference/plugin-descriptors.md) for plugin
identity, entrypoints, declared capabilities, docs, security metadata, and
compatibility. Descriptors declare needs; they do not grant runtime authority.

## Review And Probation

New or changed community plugins should start in probation. Use
[`craik.plugin_probation`](../reference/plugin-probation.md) to record review
criteria, compatibility checks, evidence, receipts, and promotion, rejection, or
expiration decisions.

Promotion should require passing required criteria and compatibility checks.
Rejected and expired plugins should preserve the decision rationale so later
agents do not repeat the same review.

## Capabilities

Plugin capability grants must be explicit and least-privilege. Use
[`craik.plugin_capability_grant`](../reference/plugin-capability-grants.md) to
scope authority to a plugin descriptor, target paths, operations, approval
requirements, and expiry.

Do not infer authority from descriptor metadata, package names, docs, or prior
successful runs. Capability grants and policy envelopes decide what a plugin may
do in the current run.

## Receipts

Every meaningful plugin action should leave a redacted receipt. Use
[`craik.plugin_receipt`](../reference/plugin-receipts.md) to link plugin actions
to descriptors, capability grants, evidence, handoffs, trust boundaries, and
results.

Receipts should summarize passed, failed, and denied actions without storing raw
secrets or unredacted plugin output.

## Reference Paths

Use [`craik.reference_integration`](../reference/reference-integrations.md) to
publish safe, reproducible examples that link docs, fixtures, checks, receipts,
and compatibility notes. Reference integrations are examples, not trust grants.

## Security Boundaries

Community plugins can execute code or trigger external effects depending on the
adapter and grants in use. Keep these boundaries explicit:

- descriptors declare metadata only;
- probation records review trust;
- capability grants authorize bounded actions;
- receipts record what happened;
- policy envelopes remain the source of runtime authority.

Do not include secrets in plugin docs, fixtures, descriptors, receipts, or
examples. Persist only redacted outputs and evidence-linked summaries.
