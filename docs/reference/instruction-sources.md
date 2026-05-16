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

## Hash State And Provenance

`craik.instruction_source_snapshot` records observed source identity with a
`sha256` content hash when the source is present. Hash status is one of:

- `unchanged`: the observed hash matches the previous known state.
- `changed`: the source exists and differs from the previous known state.
- `missing`: the declared source was not found and must not include a content
  hash.
- `new`: the source exists but has no previous known state.

`craik.instruction_provenance` links distilled material back to a source and
optional snapshot. Provenance can use a precise line range when available or a
source-level fallback when the extractor cannot identify stable lines. Partial
line ranges are invalid because they make review ambiguous.

## Distilled Instruction Categories

`craik.distilled_instruction_proposal` keeps extracted instructions reviewable.
Every proposal must cite provenance and remain inactive until a later promotion
decision approves it.

Supported categories:

| Category | Meaning |
| --- | --- |
| `instruction` | General runtime guidance for agents. |
| `policy` | Governance, approval, or authority requirement. |
| `preference` | Stable user, team, or project preference. |
| `command` | Command or validation instruction. |
| `boundary` | Scope, ownership, or authority boundary. |
| `handoff_rule` | Requirement for durable handoff content or timing. |
| `memory_rule` | Rule for memory reads, writes, proposals, or promotion. |
| `security_rule` | Security, secret, or safety-sensitive requirement. |
| `stale_risk` | Warning that prior context may become stale or unsafe. |

Policy and security-rule proposals require evidence IDs in addition to
provenance. Approved proposals must include a promoted constraint ID plus
reviewer and decision time. Rejected and deferred proposals also preserve
reviewer and decision time so future agents can see that extraction did not
silently become active runtime behavior.

## Stale Invalidation

Instruction source snapshots are compared by source ID and content hash.
Distillations are deferred when their source changes, goes missing, is newly
discovered, or is omitted from the current scan. Deferral preserves the
proposal, provenance, evidence, and previous review decision for audit, but the
proposal is excluded from automatic promotion until it is reviewed again.

Case files and onboarding reports surface stale instruction warnings so agents
do not treat outdated distilled instructions as active constraints.

## Instruction Conflicts

Distilled proposals from different sources can conflict. Craik opens local
`craik.contradiction_report` records for incompatible instruction, policy,
command, boundary, or security-rule proposals. Reports link the conflicting
proposal IDs, source IDs, and provenance IDs so a human reviewer can inspect the
source material.

Conflicting proposals are deferred and excluded from automatic promotion until
the contradiction is reviewed. Preference and stale-risk disagreements are kept
as reviewable proposals, but they do not automatically become contradiction
reports because they may represent tolerable local variation rather than
mutually exclusive runtime authority.

## Promotion Reviews

`craik.instruction_promotion_review` records approved, rejected, and deferred
promotion decisions. Reviews link policy envelopes, receipts, memory proposals,
and handoffs so promotion is auditable.

Approved reviews create `craik.promoted_instruction_constraint` records. Active
constraints retain the proposal ID, source ID, source snapshot ID, provenance
IDs, evidence IDs, and review links. Rejected and deferred reviews do not create
active constraints, and unapproved distilled proposals must not affect case-file
or policy behavior.
