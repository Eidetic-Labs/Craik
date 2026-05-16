# Instruction Sources

Instruction source registries declare which project files Craik may use for
runtime instruction distillation. Craik does not treat every Markdown file as
runtime authority.

## Supported Sources

`craik.instruction_source` supports these standard source kinds and paths:

| Kind | Path |
| --- | --- |
| `agents_md` | `AGENTS.md` |
| `claude_md` | `CLAUDE.md` |
| `gemini_md` | `GEMINI.md` |
| `hermes_md` | `HERMES.md` |
| `skills_md` | `SKILLS.md` |
| `cursor_rules` | `.cursorrules` |
| `github_copilot_instructions` | `.github/copilot-instructions.md` |
| `codex_instructions` | `.codex/instructions.md` |
| `policy_doc` | Explicitly declared project policy doc path |

Standard source kinds must use their canonical path. `policy_doc` sources are
the exception: their path is declared by the project and must be listed in the
registry's `declared_policy_doc_paths`.

## Registry Boundaries

`craik.instruction_source_registry` is project-scoped. It records declared
sources, active source IDs, and policy doc paths. Active source IDs must refer to
registered active sources.

The registry is a discovery boundary, not an approval boundary. Later
distillation and promotion steps must still preserve provenance, stale-source
state, contradiction reports, and human approval before extracted instructions
become active runtime constraints.
