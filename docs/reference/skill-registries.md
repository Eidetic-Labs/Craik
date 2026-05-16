# Skill Registries

Skill registries describe which reusable skills are available to a project and
where each skill came from.

The `craik.skill_registry` contract records project-local and global skill
entries. Each entry includes:

- `skill_package_id`;
- `scope`: `project` or `global`;
- source path;
- trust boundary;
- numeric precedence;
- active state;
- provenance links;
- declaration owner and timestamp.

Project-scoped entries require `project_id`. Global entries must omit
`project_id`. This keeps global discovery from being confused with project-local
authority.

## Precedence

Lower `precedence` values win. Active precedence values must be unique.

When a project-local and global entry reference the same skill package, the
project-local entry must outrank the global entry. The registry can also record
`precedence_order` for consumers that want a stable ordered list of active skill
entry ids.

## Provenance

Every registry entry requires provenance. Discovery should preserve the source
that caused a skill to enter the registry, such as a project skill path, a global
skill path, or an evidence record captured during onboarding.
