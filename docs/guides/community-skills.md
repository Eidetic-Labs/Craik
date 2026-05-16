# Community Skills

Community skills package reusable instructions, examples, and optional assets
for a bounded workflow. They should be easy to inspect before use and safe to
run under Craik policy.

## Authoring

A community skill should include:

- a clear `SKILL.md` entrypoint;
- a versioned skill package record;
- expected input and output schemas;
- docs for intended use and limitations;
- provenance for copied, generated, or externally sourced material;
- examples or fixtures that can be validated locally.

Use [`craik.skill_package`](../reference/skill-packages.md) for package
metadata. Use [`craik.skill_registry`](../reference/skill-registries.md) to
record whether a skill is project-local or global and how precedence is resolved.

## Scoping

Project-local skills should live with the project and use a project trust
boundary. Global skills should be treated as user-supplied defaults. If both a
project-local and global skill describe the same package, the project-local
entry should take precedence.

Skill invocation context is per-run state. Use
[`craik.skill_invocation_context`](../reference/skill-contexts.md) to record
inputs, outputs, omissions, policy links, receipts, and evidence for one
invocation.

## Review

Review community skills before adopting them:

- confirm the package version and entrypoints;
- inspect docs and examples;
- verify expected input and output schemas;
- check provenance links;
- confirm the skill does not claim runtime authority;
- run local checks for linked fixtures or examples.

Reference integrations can document known-good skill examples. See
[`craik.reference_integration`](../reference/reference-integrations.md) for the
fixture and check structure.

## Security Boundaries

Skills are instructions and supporting assets. They do not grant shell, network,
repository, memory, or GitHub authority. Runtime authority must come from policy
and capability grants. Treat unreviewed community skills as untrusted input until
their provenance, docs, and expected outputs have been checked.

Do not place secrets in skill docs, fixtures, examples, or assets. Persisted
skill invocation context should be redacted and evidence-linked.
