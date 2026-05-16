# Adapter Packages

Adapter packages describe runner adapter distribution metadata.

The `craik.adapter_package` contract records:

- adapter identity and package version;
- adapter implementation entrypoints;
- capability surfaces exposed by the adapter;
- Craik, runner mode, Python, and platform compatibility;
- linked runner metadata and plugin descriptors when applicable;
- docs, provenance, and version constraints.

Adapter packages do not grant runtime authority. They describe how a runner
adapter can be loaded and what surfaces it may expose. Policy envelopes and
capability grants still decide what a run may do.

## Expectations

Adapter packages require at least one entrypoint, one capability surface, docs,
and provenance. Package versions must be version-like, and compatibility must
name at least one supported runner mode.
