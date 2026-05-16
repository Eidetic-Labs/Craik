# Plugin Descriptors

Plugin descriptors define governed plugin metadata without granting runtime
authority.

The `craik.plugin_descriptor` contract records:

- identity: `id`, `name`, `publisher`, and `plugin_version`;
- entrypoints: command, module, workflow, service, or docs paths exposed by the plugin;
- capability declarations: requested capabilities, operations, targets, risk, and whether an explicit grant is required;
- docs and security notes required for review;
- compatibility metadata for Craik versions, Python versions, platforms, and support status;
- optional links to skill packages and provenance records.

Descriptors are declarations. They do not authorize execution, file writes,
network access, memory access, or GitHub operations. Runtime authority remains
separate in `craik.capability_grant` and must be checked before a runner invokes
plugin behavior.

## Validation

Craik rejects plugin descriptors that:

- omit entrypoints, capabilities, docs, security notes, or compatibility metadata;
- use a non-version-like `plugin_version`;
- set `runtime_authority` to true;
- declare high or critical risk capabilities without requiring explicit grants.

This keeps plugin discovery and review independent from policy decisions about
what the current run is allowed to do.
