# Roadmap

This roadmap is executable by design. Every roadmap item must produce implementation, tests or validation, and documentation. Craik should not ship features that only exist as code or only exist as strategy.

Craik's product goal is a durable agent runtime for shared project models and governed multi-agent work. The roadmap therefore prioritizes the smallest useful runtime first, then expands into Stigmem-native memory, runner adapters, multi-agent coordination, instruction distillation, and community extensions.

## Roadmap Rules

1. **Every feature has docs.** User-facing behavior requires guide docs. Runtime contracts require reference docs. Policy behavior requires security/governance docs. Adapter behavior requires integration docs.
2. **Docs ship with implementation.** A feature is not done until its docs, examples, and validation guidance are merged.
3. **Strict by default.** New capabilities must respect policy envelopes, grants, redaction, receipts, and memory-write defaults.
4. **Evidence before memory.** No durable assertion or Stigmem write without evidence, provenance, and scope.
5. **Source remains canonical.** Derived memory, distilled instructions, generated docs, and summaries must cite source artifacts.
6. **CLI first, UI later.** CLI workflows prove the runtime before dashboard work broadens the surface.
7. **Stigmem is the reference substrate.** Local mode exists for onboarding and tests, but full durable behavior assumes Stigmem.

## Documentation Model

Craik documentation should borrow the most useful patterns from durable-memory systems, local agent runtimes, and multi-agent orchestration tools.

From Stigmem:

- explicit concept docs,
- protocol and contract reference docs,
- generated API/CLI reference when implementation exists,
- roadmap and limitations docs,
- security and governance docs,
- durable examples tied to real workflows,
- clear public/internal boundaries.

From local agent runtimes:

- practical setup docs,
- workspace/project mental model,
- tool/skill/plugin docs,
- channel/adapter docs,
- operator-friendly examples.

From multi-agent orchestration tools:

- CLI-first user guides,
- configuration docs,
- skills docs,
- security/approval docs,
- multi-agent workflow docs,
- exact dependency and supply-chain notes where relevant.

Target docs tree:

```text
docs/
  concepts/
    durable-agent-runtime.md
    project-models.md
    case-files.md
    handoffs.md
    receipts.md
    work-graph.md
    memory-and-stigmem.md
    governance.md
    instruction-distillation.md
    skills-and-plugins.md
  guides/
    installation.md
    quickstart.md
    first-stigmem-reconciliation-demo.md
    configuring-craik-home.md
    connecting-stigmem.md
    using-case-files.md
    writing-handoffs.md
    running-policy-tests.md
    runner-adapters.md
    community-skills.md
    community-plugins.md
  reference/
    cli.md
    config.md
    schemas.md
    policy-profiles.md
    memory-backends.md
    runner-adapter-contract.md
    plugin-contract.md
  security/
    index.md
    redaction.md
    secrets.md
    capability-grants.md
    fail-open-profiles.md
  roadmap.md
  limitations.md
```

Root-level project governance files remain authoritative for contribution, security disclosure, trademarks, and maintainership.

## Release Gates

Craik should remain on `0.x.0` releases until the maintainers are very confident that the product is stable enough to call `1.0`. The gates below are sequencing targets, not promises that `1.0.0` follows immediately after `0.7.0`. Additional `0.x.0` releases should be added whenever the product needs more soak time, compatibility work, security hardening, or real-user validation.

### v0.1.0 Gate: Durable Single-Agent Runtime

`v0.1.0` must prove Craik's core value without requiring the full north-star surface.

Required outcome:

> A single agent can register a real repo, assemble a governed case file, use Stigmem-backed memory context, perform the Stigmem documentation reconciliation demo, record receipts, produce a durable handoff, and leave memory proposals without relying on chat history.

Required capabilities:

- Python 3.12+ package and `craik` CLI.
- MIT license and governance files.
- `~/.craik` local home and `CRAIK_HOME` override.
- Pydantic runtime contracts.
- SQLite local state.
- project registry.
- strict policy profile, trusted-local profile, automation profile.
- capability grants.
- central redaction utility.
- receipt store.
- handoff writer.
- local memory backend.
- Stigmem backend with required endpoint compatibility.
- case file assembler.
- evidence references.
- assumption ledger.
- context budget metadata.
- intent lock.
- self-audit before handoff.
- memory proposal flow.
- memory diff for local proposals and Stigmem writes.
- work graph export for task, handoff, receipt, fact/proposal, evidence, and contradiction nodes.
- GitHub read adapter.
- first demo workflow for Stigmem docs reconciliation.
- agent-native onboarding for the demo project.
- policy tests for the core security baseline.

Explicitly not required for `v0.1.0`:

- full autonomous multi-agent orchestration,
- production UI,
- hosted service,
- community marketplace,
- complete Codex/Claude/Gemini execution control,
- automatic Stigmem conflict resolution,
- full plugin runtime.

`v0.1.0` should still define contracts and docs that make those later features possible.

### v0.2.0 Gate: Runner Adapter Preview

Required outcome:

> Codex, Claude, and Gemini can consume Craik case files and return normalized handoffs/results through first-class adapter contracts.

Required capabilities:

- runner adapter interface,
- Codex adapter,
- Claude adapter,
- Gemini adapter,
- runner capability matrix,
- policy-aware prompt compiler,
- real-runner contract test fixtures,
- runner metadata in receipts and handoffs,
- runner trust boundaries,
- runner-specific onboarding output.

### v0.3.0 Gate: Single-Agent Execution Loop

Required outcome:

> Craik can drive one agent through a governed plan/act/observe/evaluate loop without relying on an untracked chat transcript.

Required capabilities:

- task run state machine,
- run id and run status model,
- plan/act/observe/evaluate/continue/stop phases,
- runner step contract,
- max-iteration controls,
- time and budget controls,
- intent-lock stop-condition enforcement,
- policy approval checks before each side effect,
- receipts per action or step,
- observed output capture,
- memory proposal creation during or after the loop,
- handoff on completion, block, failure, or interruption,
- resumable interrupted runs,
- run inspection command,
- run recovery command,
- agent exit discipline.

The LLM remains the reasoning engine, but Craik owns the loop boundary, persistence, policy gates, receipts, and stop conditions.

### v0.4.0 Gate: Multi-Agent Review And Coordination

Required outcome:

> Craik can coordinate role-specific agents, preserve specialist outputs, and structure disagreement without flattening unresolved contradictions.

Required capabilities:

- orchestrator role,
- specialist roles,
- implementer/verifier/adversarial reviewer/policy reviewer/docs reviewer/memory curator/adjudicator roles,
- typed worker results,
- parallel read-only investigations,
- structured agent debate,
- contradiction reports,
- human delegation points,
- cross-agent review protocol,
- scope-change protocol.

### v0.5.0 Gate: Runtime Instruction Distillation

Required outcome:

> Craik can distill declared runtime instruction files into provenance-linked proposals and use them safely in case files, policies, and onboarding.

Required capabilities:

- declared instruction source registry,
- support for `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `HERMES.md`, `SKILLS.md`, `.cursorrules`, `.github/copilot-instructions.md`, `.codex/instructions.md`, and declared policy docs,
- source hash tracking,
- line/range provenance where available,
- instruction/policy/preference/command/boundary/handoff-rule/memory-rule/security-rule/stale-risk extraction categories,
- stale distillation invalidation,
- contradiction reports between instruction sources,
- approval flow for promoted constraints.

### v0.6.0 Gate: Quality, Continuity, And Recovery

Required outcome:

> Craik helps agents recover, improve handoffs, avoid stale context, and explain what changed between runs.

Required capabilities:

- recovery mode,
- runtime critic,
- red team mode,
- handoff quality score,
- evidence coverage score,
- context debt tracking,
- tool result attestation,
- knowledge freshness probes,
- evidence expiration rules,
- known traps,
- negative knowledge,
- scratchpad with expiry,
- first-class unknowns,
- structured context requests,
- "what changed since last time" deltas,
- agent exit discipline.

### v0.7.0 Gate: Skills, Plugins, And Ecosystem Foundations

Required outcome:

> Craik can support reusable skills and governed plugins without weakening the runtime security model.

Required capabilities:

- skill package format,
- project-scoped and global skills,
- context contracts for skills,
- plugin descriptor format,
- probationary plugins,
- plugin capability grants,
- plugin receipts,
- adapter packages,
- reference integrations,
- community skills docs,
- community plugins docs.

### v0.8.0 Gate: Operator Experience

Required outcome:

> Operators can inspect project state without reading raw logs.

Required capabilities:

- dashboard or TUI decision,
- work graph explorer,
- handoff viewer,
- receipt viewer,
- contradiction inbox,
- evidence and assumption views,
- delegation queue,
- budget/quota view,
- instruction distillation view,
- quality gate view,
- memory impact preview,
- known traps view,
- run delta view.

### v0.9.0 Gate: Operator Integrations And Always-On Gateway

Required outcome:

> Craik can run as an always-on operator service with controlled ingress from external channels.

Required capabilities:

- gateway daemon mode,
- `craik setup` wizard,
- `craik doctor` diagnostics,
- `craik update` or update guidance,
- channel adapter contract,
- first messaging channel adapter,
- inbound identity and pairing model,
- channel allowlists,
- channel-scoped policy envelopes,
- webhook ingress,
- scheduled automations,
- cron-like task creation,
- gateway receipts,
- gateway troubleshooting docs.

Explicitly deferred until this phase or later:

- broad channel matrix,
- consumer assistant positioning,
- open inbound DM behavior,
- and mobile companion surfaces.

### v0.10.0 Gate: Execution Environments, Sandboxes, And Provider Routing

Required outcome:

> Craik can choose model/provider/runtime execution paths and enforce environment boundaries explicitly.

Required capabilities:

- model provider registry,
- model/provider switching UX,
- provider failover policy,
- provider budget and quota links,
- MCP client integration,
- MCP server/export decision,
- sandbox backend contract,
- local process backend,
- Docker sandbox backend,
- SSH or remote shell backend,
- browser/tool execution boundary,
- environment capability receipts,
- sandbox policy tests,
- provider routing docs.

### v0.11.0 Gate: Self-Improving Skills And Learning Loops

Required outcome:

> Craik can improve reusable operating guidance without allowing agents to silently rewrite their own authority.

Required capabilities:

- skill performance telemetry,
- autonomous skill proposal creation,
- skill improvement proposals,
- skill eval/replay harness,
- periodic memory review nudges,
- user/team preference modeling as reviewable facts,
- learning-loop receipts,
- approval gates for promoted skills,
- rollback path for bad skill updates,
- training/trajectory export format,
- trajectory compression or summarization,
- learning-loop docs.

This phase should build on instruction distillation and the skill/plugin system. Agents may propose changes to skills, but those changes must remain reviewable until policy allows promotion.

### v0.12.0 Gate: Multimodal And Companion Surfaces

Required outcome:

> Craik can expose durable agent work through richer operator surfaces without compromising its policy and evidence model.

Required capabilities:

- voice input/output posture,
- speech-to-text adapter contract,
- text-to-speech adapter contract,
- multimodal artifact references,
- desktop companion app decision,
- mobile companion app decision,
- live visual workspace/canvas decision,
- work graph to visual workspace bridge,
- accessibility requirements,
- companion app security docs,
- multimodal redaction tests.

This phase is optional unless Craik deliberately competes with personal-assistant surfaces. It should not block server-side software-delivery workflows.

### v0.13.0 Gate: Migration, Internationalization, And Ecosystem Compatibility

Required outcome:

> Teams can adopt Craik from adjacent tools and operate it in broader language and ecosystem contexts.

Required capabilities:

- adjacent-tool import/migration assessment,
- multi-agent tool import/migration assessment,
- import dry-run reports,
- memory/skill/config migration maps,
- secret migration policy,
- MCP ecosystem compatibility guide,
- adjacent-runtime bridge decision,
- multi-agent workflow bridge decision,
- locale/i18n framework,
- translated docs strategy,
- ecosystem compatibility tests.

### Future 1.0 Graduation Gate: Professional Agent Runtime

Required outcome:

> Craik is stable enough for external teams to use for real multi-agent software delivery workflows.

This is a graduation gate, not a scheduled release. Craik should continue shipping `0.x.0` releases until this bar is clearly met by real usage, documentation maturity, compatibility confidence, and security posture.

Required capabilities:

- stable core schemas,
- migration path for persisted state,
- SemVer release process,
- package publication,
- security release process,
- complete generated CLI/reference docs,
- production-quality Stigmem integration,
- documented limits and failure modes,
- runnable demo,
- community contribution path,
- at least one complete runner adapter supported end to end,
- policy tests in CI,
- public/internal boundary classifier,
- provenance-aware documentation workflow,
- memory hygiene workflow,
- work product classification,
- decision record suggestions,
- learning without self-trust.

Confidence requirements before `1.0.0`:

- at least one complete runner adapter has been used successfully on real workflows,
- Stigmem-backed memory has soaked on real projects,
- persisted schema migrations have been exercised,
- security and redaction behavior has been tested under realistic agent runs,
- documentation is complete enough for external users without maintainer hand-holding,
- community contribution and support expectations are clear,
- and known limitations are documented honestly.

## Executable Workstreams

Each workstream below should become one or more GitHub milestones/issues. Documentation requirements are part of the definition of done.

### 0. Project Foundation

Scope:

- package metadata,
- Python 3.12+ project skeleton,
- `craik` CLI,
- MIT license,
- governance files,
- dependency lock strategy,
- CI quality gates,
- package-name reservation or publication.

Validation:

- `craik --version` works,
- tests run in CI,
- lint/type checks run in CI,
- package metadata validates.

Docs required:

- installation guide,
- quickstart stub,
- contribution guide updates,
- release/support note,
- limitations note for pre-`0.1.0`.

### 1. Runtime Contracts

Scope:

- task request,
- project profile,
- policy envelope,
- capability grant,
- capability receipt,
- case file,
- agent role,
- worker result,
- handoff,
- memory proposal,
- memory backend capabilities,
- contradiction report,
- work graph event,
- evidence reference,
- assumption,
- delegation point,
- intent lock,
- instruction distillation item,
- quality gate result,
- artifact classification.

Validation:

- schema fixtures,
- invalid fixture tests,
- JSON serialization tests,
- version field tests.

Docs required:

- schema reference,
- examples for each contract,
- versioning and migration policy.

### 2. Local State And Project Registry

Scope:

- `~/.craik` default home,
- `CRAIK_HOME` override,
- `config/`, `secrets/`, `state/`, `cache/`, `logs/`, `receipts/`, `handoffs/`, `case-files/`, `projects/`,
- secure permissions where supported,
- SQLite store,
- project registry,
- immutable path config,
- project-local `.craik/` explicit opt-in only.

Validation:

- path resolver tests,
- permission tests where portable,
- registry persistence tests,
- project-local opt-in tests.

Docs required:

- configuring Craik home,
- local state layout reference,
- secrets handling guide.

### 3. Policy, Grants, Redaction, And Receipts

Scope:

- strict profile,
- trusted-local profile,
- automation profile,
- fail-open profile visibility,
- capability grants,
- immutable path protection,
- central redaction utility,
- shell/file/GitHub/memory grant enforcement,
- receipt persistence,
- policy denial receipts.

Validation:

- policy fixture tests,
- redaction tests,
- immutable path tests,
- fail-open receipt tests,
- automation fail-closed tests.

Docs required:

- policy profiles reference,
- fail-open guide,
- capability grants guide,
- redaction and secrets docs.

### 4. Case Files, Intent, Evidence, And Assumptions

Scope:

- task intent lock,
- repository state ingestion,
- docs and ADR discovery,
- Stigmem/local fact loading,
- GitHub context placeholders,
- evidence references,
- assumption ledger,
- context budget metadata,
- stale-risk markers,
- context explanations,
- structured context requests,
- first-class unknowns,
- context debt tracking.

Validation:

- deterministic fixture output,
- evidence reference tests,
- assumption promotion tests,
- context inclusion/exclusion tests,
- stale-risk tests.

Docs required:

- case file concept doc,
- using case files guide,
- evidence and assumptions guide,
- context budgeting guide.

### 5. Handoffs, Self-Audit, And Exit Discipline

Scope:

- structured handoff,
- Markdown handoff,
- self-audit before handoff,
- incomplete run handoff,
- handoff quality score,
- unresolved questions,
- next steps,
- receipt links,
- memory proposal links,
- context debt links.

Validation:

- handoff schema tests,
- self-audit checklist tests,
- quality score fixture tests,
- interrupted-run fixture tests.

Docs required:

- handoff concept doc,
- writing handoffs guide,
- self-audit reference,
- recovery and incomplete run guide.

### 6. Memory Backends And Stigmem Integration

Scope:

- ephemeral backend,
- local backend,
- Stigmem backend,
- Stigmem capability detection,
- health and metadata checks,
- fact query/list/get/write,
- provenance reads,
- optional recall,
- optional conflicts,
- local proposal model,
- memory diff,
- memory impact preview,
- source identity handling,
- source attestation handling,
- error mapping.

Validation:

- backend interface tests,
- local backend persistence tests,
- Stigmem integration tests against a local node,
- auth failure tests,
- optional capability fallback tests,
- memory diff tests.

Docs required:

- memory backend reference,
- connecting Stigmem guide,
- Stigmem compatibility matrix,
- memory proposal and promotion guide,
- memory impact preview guide.

### 7. GitHub Adapter And Demo Workflow

Scope:

- GitHub auth detection,
- repository metadata,
- issues,
- PRs,
- changed files,
- check status,
- guarded GitHub comments/issues/PR creation,
- first Stigmem docs reconciliation demo.

Validation:

- mocked GitHub adapter tests,
- read-only fallback tests,
- permission failure tests,
- fixture demo run.

Docs required:

- GitHub adapter guide,
- first Stigmem reconciliation demo,
- public/internal boundary guidance,
- troubleshooting guide.

### 8. Work Graph, Contradictions, And Delegation

Scope:

- graph nodes and edges,
- task/handoff/fact/proposal/receipt/evidence/assumption/delegation/artifact nodes,
- contradiction reports,
- Stigmem conflict linking,
- local contradiction reports,
- human delegation points,
- approval/clarification/policy override/memory promotion/release signoff requests.

Validation:

- graph export tests,
- contradiction lifecycle tests,
- delegation lifecycle tests,
- unresolved delegation blocks tests.

Docs required:

- work graph concept doc,
- contradiction inbox guide,
- human delegation guide,
- graph export reference.

### 9. Agent-Native Onboarding

Scope:

- `craik onboard --project <project-id>`,
- project model,
- active policies,
- ADRs and immutable paths,
- docs boundaries,
- recent handoffs,
- unresolved contradictions,
- stale-risk warnings,
- validation commands,
- Stigmem status,
- known traps,
- allowed next actions.

Validation:

- onboarding fixture tests,
- missing context tests,
- stale context tests,
- runner-readable output tests.

Docs required:

- onboarding guide,
- known traps guide,
- project model concept doc.

### 10. Runner Adapters

Scope:

- runner adapter interface,
- Codex adapter,
- Claude adapter,
- Gemini adapter,
- runner capability matrix,
- policy-aware prompt compiler,
- runner metadata,
- normalized worker results,
- normalized handoffs,
- real-runner contract tests,
- runner trust profiles.

Validation:

- adapter interface tests,
- fixture contract tests,
- prompt compilation tests,
- runner capability matrix tests,
- real-runner smoke tests when credentials/tools are available.

Docs required:

- runner adapter contract,
- Codex adapter guide,
- Claude adapter guide,
- Gemini adapter guide,
- prompt compiler reference,
- runner capability matrix reference.

### 11. Single-Agent Execution Loop

Scope:

- run id and run status model,
- task run state machine,
- plan/act/observe/evaluate/continue/stop phases,
- runner step contract,
- max-iteration limit,
- timeout and budget limits,
- intent-lock stop-condition enforcement,
- approval and grant checks before side effects,
- step receipts,
- observed output capture,
- memory proposal hooks,
- handoff on completion/block/failure/interruption,
- run resume,
- run recovery,
- agent exit discipline.

Validation:

- state-machine transition tests,
- max-iteration and timeout tests,
- budget exhaustion tests,
- stop-condition enforcement tests,
- approval-block tests,
- receipt-per-step tests,
- interrupted run resume tests,
- handoff-on-failure tests,
- runner fixture tests.

Docs required:

- single-agent execution loop concept doc,
- running tasks guide,
- run state reference,
- resume and recovery guide,
- loop policy guide.

### 12. Multi-Agent Coordination

Scope:

- orchestrator,
- specialist tasks,
- parallel read-only investigations,
- implementer/verifier/adversarial reviewer/policy reviewer/docs reviewer/memory curator/release reviewer/adjudicator roles,
- typed worker results,
- cross-agent review protocol,
- structured agent debate,
- scope-change protocol.

Validation:

- child task graph tests,
- typed worker result tests,
- debate/adjudication fixture tests,
- unresolved contradiction block tests,
- scope-change proposal tests.

Docs required:

- multi-agent workflows guide,
- role reference,
- review protocol guide,
- structured debate guide.

### 13. Runtime Instruction Distillation

Scope:

- declared instruction source registry,
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `HERMES.md`, `SKILLS.md`, `.cursorrules`, `.github/copilot-instructions.md`, `.codex/instructions.md`,
- source hash tracking,
- line/range provenance,
- extraction categories,
- distillation proposals,
- stale distillation invalidation,
- instruction contradiction reports,
- promotion approval.

Validation:

- Markdown fixture tests,
- source hash invalidation tests,
- extraction category tests,
- contradiction fixture tests,
- approval/promotion tests.

Docs required:

- instruction distillation concept doc,
- declaring instruction sources guide,
- distillation review guide,
- instruction categories reference.

### 14. Quality Gates And Freshness

Scope:

- runtime critic,
- red team mode,
- evidence coverage score,
- tool result attestation,
- knowledge freshness probes,
- evidence expiration rules,
- negative knowledge,
- runtime memory hygiene,
- decision record suggestions,
- learning without self-trust.

Validation:

- critic fixture tests,
- red team policy tests,
- evidence coverage tests,
- tool-result source tests,
- freshness probe tests,
- memory hygiene proposal tests.

Docs required:

- quality gates guide,
- freshness and staleness guide,
- negative knowledge guide,
- memory hygiene guide,
- decision record suggestion guide.

### 15. Budgets, Quotas, And Operational Bounds

Scope:

- context token budgets,
- model spend budgets,
- wall-clock budgets,
- shell command count,
- GitHub write count,
- memory write count,
- parallel worker count,
- retry count,
- approval count,
- budget receipts,
- budget escalation/block behavior.

Validation:

- budget accounting tests,
- exhaustion behavior tests,
- fail-open budget receipt tests,
- policy profile budget tests.

Docs required:

- budget and quota guide,
- policy budget reference,
- troubleshooting budget exhaustion.

### 16. Recovery And Continuity

Scope:

- recovery mode,
- partial receipt loading,
- scratchpad restore,
- changed file detection,
- unfinished handoff recovery,
- unresolved delegation restore,
- "what changed since last time" deltas,
- run delta summaries.

Validation:

- interrupted-run fixtures,
- recovery command tests,
- delta calculation tests,
- partial handoff tests.

Docs required:

- recovery guide,
- run deltas guide,
- interruption handling reference.

### 17. Artifact And Documentation Intelligence

Scope:

- work product classification,
- provenance-aware documentation,
- public/internal boundary classifier,
- generated doc evidence links,
- docs stale-state detection,
- release note classification,
- audit artifact classification.

Validation:

- classifier fixture tests,
- public/internal boundary tests,
- provenance link tests,
- stale doc fixture tests.

Docs required:

- artifact classification reference,
- provenance-aware docs guide,
- public/internal boundary guide,
- docs maintenance guide.

### 18. Skills, Plugins, And Community Ecosystem

Scope:

- skill package format,
- project-scoped skills,
- global skills,
- community skills layout,
- plugin descriptor format,
- probationary plugin policy,
- plugin capability grants,
- plugin receipts,
- adapter package guidance,
- reference integrations,
- marketplace/index format decision.

Validation:

- skill loader tests,
- plugin descriptor validation tests,
- probationary policy tests,
- plugin receipt tests,
- community package fixture tests.

Docs required:

- skills concept doc,
- writing skills guide,
- community skills guide,
- plugin contract reference,
- writing plugins guide,
- plugin security guide,
- marketplace/index guide.

### 19. Operator Experience

Scope:

- TUI/dashboard decision,
- work graph explorer,
- handoff viewer,
- receipt viewer,
- contradiction inbox,
- evidence and assumption views,
- delegation queue,
- budget view,
- instruction distillation view,
- quality gate view,
- memory impact preview,
- known traps view,
- run delta view.

Validation:

- UI/TUI smoke tests,
- nonblank rendering checks where applicable,
- fixture state rendering tests,
- accessibility and keyboard navigation checks for UI surfaces.

Docs required:

- operator guide,
- dashboard/TUI guide,
- view reference,
- troubleshooting guide.

### 20. Operator Integrations And Always-On Gateway

Scope:

- gateway daemon mode,
- setup wizard,
- diagnostics command,
- update guidance,
- channel adapter contract,
- first messaging channel adapter,
- inbound identity and pairing model,
- channel allowlists,
- channel-scoped policy envelopes,
- webhook ingress,
- scheduled automations,
- gateway receipts.

Validation:

- daemon lifecycle tests,
- setup wizard fixture tests,
- diagnostics failure-mode tests,
- webhook signature tests,
- channel identity mapping tests,
- scheduled task creation tests,
- gateway receipt tests.

Docs required:

- gateway guide,
- setup guide,
- diagnostics guide,
- channel adapter reference,
- webhook reference,
- scheduler guide,
- gateway security guide.

### 21. Execution Environments, Sandboxes, And Provider Routing

Scope:

- model provider registry,
- provider switching UX,
- provider failover policy,
- provider budget and quota links,
- MCP client integration,
- MCP server/export decision,
- sandbox backend contract,
- local process backend,
- Docker sandbox backend,
- SSH or remote shell backend,
- browser/tool execution boundary,
- environment capability receipts.

Validation:

- provider registry tests,
- provider failover tests,
- MCP compatibility fixture tests,
- sandbox policy tests,
- backend isolation tests,
- environment receipt tests,
- budget linkage tests.

Docs required:

- provider routing guide,
- provider config reference,
- MCP integration guide,
- sandbox backend reference,
- execution environment security guide.

### 22. Self-Improving Skills And Learning Loops

Scope:

- skill performance telemetry,
- autonomous skill proposal creation,
- skill improvement proposals,
- skill eval/replay harness,
- periodic memory review nudges,
- user/team preference facts,
- learning-loop receipts,
- approval gates for promoted skills,
- rollback path for bad skill updates,
- training/trajectory export format,
- trajectory compression or summarization.

Validation:

- skill proposal tests,
- skill eval fixture tests,
- replay determinism tests,
- approval gate tests,
- rollback tests,
- trajectory export tests,
- learning-loop receipt tests.

Docs required:

- skill improvement guide,
- learning-loop policy guide,
- skill eval reference,
- trajectory export reference,
- rollback guide.

### 23. Multimodal And Companion Surfaces

Scope:

- voice input/output posture,
- speech-to-text adapter contract,
- text-to-speech adapter contract,
- multimodal artifact references,
- desktop companion app decision,
- mobile companion app decision,
- live visual workspace/canvas decision,
- work graph to visual workspace bridge,
- accessibility requirements.

Validation:

- multimodal artifact schema tests,
- redaction tests for transcript and media metadata,
- accessibility checks for companion surfaces,
- visual workspace smoke tests where implemented,
- adapter contract tests.

Docs required:

- multimodal posture doc,
- voice adapter reference,
- companion app security guide,
- visual workspace guide,
- accessibility checklist.

### 24. Migration, Internationalization, And Ecosystem Compatibility

Scope:

- adjacent-tool import/migration assessment,
- multi-agent workflow import/migration assessment,
- import dry-run reports,
- memory/skill/config migration maps,
- secret migration policy,
- ecosystem compatibility guide,
- adjacent runtime bridge decision,
- multi-agent workflow bridge decision,
- locale/i18n framework,
- translated docs strategy.

Validation:

- import dry-run fixture tests,
- migration map tests,
- secret redaction tests,
- bridge compatibility smoke tests where implemented,
- locale fallback tests,
- translated docs link tests where applicable.

Docs required:

- migration guide,
- import dry-run reference,
- secret migration policy,
- ecosystem compatibility guide,
- i18n guide,
- bridge decision records.

## v0.1.0 Issue Cut

The initial issue set should cover only the `v0.1.0` gate and any contracts needed to avoid rework.

Recommended issues:

1. Scaffold Python package and `craik` CLI.
2. Add core Pydantic schemas and fixtures.
3. Implement `~/.craik` path resolver and local state layout.
4. Implement SQLite local store.
5. Implement project registry.
6. Implement strict/trusted-local/automation policy profiles.
7. Implement capability grants and immutable path protection.
8. Implement central redaction utility.
9. Implement receipt store.
10. Implement case file assembler with evidence, assumptions, and context budget metadata.
11. Implement intent lock.
12. Implement handoff writer and self-audit checklist.
13. Implement local memory backend and proposal flow.
14. Implement Stigmem backend minimum compatibility.
15. Implement memory diff and memory impact preview foundations.
16. Implement GitHub read adapter.
17. Implement work graph export.
18. Implement contradiction report model.
19. Implement agent-native onboarding.
20. Implement policy test harness and core policy tests.
21. Implement Stigmem documentation reconciliation demo.
22. Build initial docs tree and publish v0.1.0 user/concept/reference docs.

Each issue should include:

- implementation checklist,
- test/validation checklist,
- documentation checklist,
- security/policy impact,
- Stigmem fact update requirement when relevant.

## Documentation Definition Of Done

Every issue must answer:

- What concept changed?
- What user workflow changed?
- What CLI/API/config changed?
- What policy or security behavior changed?
- What examples should exist?
- What limitations apply?
- What facts should future agents know?

For implementation issues, docs should be updated in the same PR unless the issue is explicitly internal-only scaffolding.

## Release Definition Of Done

Every release must include:

- passing tests,
- passing lint/type checks,
- generated or updated CLI/reference docs,
- updated roadmap state,
- updated limitations,
- security notes,
- migration notes when local state or schemas change,
- runnable demo status,
- and a Stigmem fact summarizing the release state.
