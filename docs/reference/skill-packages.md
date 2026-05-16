# Skill Packages

Skill packages describe reusable instructions, entrypoints, docs, and assets.
They do not carry plugin runtime authority.

`craik.skill_package` records:

- package id, name, version, and description,
- one or more entrypoints,
- expected input and output schemas,
- documentation files,
- asset paths,
- provenance links,
- and an optional plugin descriptor link.

Skill packages must include docs and at least one entrypoint. Runtime authority
is always `false`; any executable authority must be represented through the
separate plugin governance and grant model.
