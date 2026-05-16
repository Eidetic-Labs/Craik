# Reference Integrations

Reference integrations describe safe, reproducible examples for skills,
plugins, and adapters.

The `craik.reference_integration` contract records:

- integration kind: `skill`, `plugin`, or `adapter`;
- the matching skill package, plugin descriptor, or adapter package id;
- docs and fixture paths;
- check commands;
- receipt links when relevant;
- compatibility notes;
- provenance.

Reference integrations must be safe to run locally and reproducible. They are
examples and validation fixtures, not durable trust grants.

## Scope

Use reference integrations to show known-good paths through the ecosystem:

- a skill package with instructions and expected contracts;
- a plugin descriptor plus receipts and checks;
- an adapter package with compatibility and runner metadata links.

Each reference should include enough docs, fixtures, and checks for another
agent to rerun it without relying on private state.
