# Feature Specification

<p className="craik-meta"><span>12 min read</span><span>For implementers</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The implementable feature surface. Every numbered feature names its
purpose, the MVP behavior the runtime ships, and the acceptance
criteria that must hold for the feature to count as done.

</div>

<div className="craik-keypoint">

**This doc turns Craik's product ideas into implementable features.**

Each feature is independently shippable but composes with the rest of
the runtime through stable contracts. Acceptance criteria are the
durable check — implementations are free to evolve as long as the
criteria still hold.

</div>

## Feature 1: Project registry

**Purpose:** Store known projects and their runtime configuration.

**MVP behavior:** `craik project add <path>` creates a project profile ·
profile records repo path, default branch, docs paths, immutable paths,
memory backend · profile is printable as JSON.

<ol className="craik-steps">
<li>A project can be added from a local Git repo.</li>
<li>Invalid paths fail with clear errors.</li>
<li>Immutable doc paths can be configured.</li>
<li>Project-profile schema validates.</li>
</ol>

## Feature 2: Case-file assembler

**Purpose:** Build task-specific context before execution.

**Inputs:** task request · project profile · repository state · docs
snippets · repository discovery defaults + project/user
include/exclude overrides · ADR/policy snippets · GitHub state (when
configured) · Stigmem facts (when configured) · recent handoffs.

**Outputs:** case file JSON · human-readable Markdown case file ·
stale-risk list · contradiction list · context inclusion/exclusion/
omission metadata · verification plan.

<ol className="craik-steps">
<li>Case-file generation is deterministic for test fixtures.</li>
<li>Generated, dependency, build, cache, and archive-heavy paths are excluded by default.</li>
<li>Project and user overrides can extend, replace, or explicitly include paths from the defaults.</li>
<li>Excluded and omitted paths are visible in context metadata.</li>
<li>Immutable ADR paths are clearly labeled.</li>
<li>Memory facts include source and confidence.</li>
<li>Stale-risk warnings are separated from verified facts.</li>
<li>Output can be consumed by an agent prompt.</li>
</ol>

## Feature 3: Policy envelope

**Purpose:** Define execution authority and obligations.

**MVP behavior:** read-only tasks default to repo-read, memory-read,
and receipt-write · implementation tasks require explicit write grants
· immutable paths cannot be written unless policy explicitly allows it
· memory writes default to proposals unless configured for direct
write · strict mode is the default profile · fail-open is profile-gated
· fail-open appears in case files, receipts, and handoffs.

<ol className="craik-steps">
<li>Denied file writes are blocked.</li>
<li>Denied memory writes become proposals.</li>
<li>Policy envelope is included in the case file.</li>
<li>Policy failures create receipts.</li>
<li>Trusted-local fail-open requires explicit opt-in.</li>
<li>Automation mode fails closed instead of widening permissions.</li>
</ol>

## Feature 4: Capability receipts

**Purpose:** Record important actions in a concise, queryable form.

**Receipt-producing actions:** file writes · shell commands · GitHub
writes · memory writes · approvals · policy denials · contradiction
opens/resolutions · handoff creation.

<ol className="craik-steps">
<li>Receipts are persisted locally.</li>
<li>Receipts can be listed by task.</li>
<li>Receipt IDs appear in handoffs.</li>
<li>Receipts include actor, capability, target, reason, result, and timestamp.</li>
<li>Receipts include policy profile and fail-open status.</li>
<li>Receipt payloads are redacted before persistence.</li>
</ol>

## Feature 5: Handoff writer

**Purpose:** Make agent work reusable by future agents.

**MVP behavior:** generate structured JSON handoff · generate Markdown
handoff · link receipts · include memory proposals · include unresolved
questions and next steps.

<ol className="craik-steps">
<li>Every completed task has a handoff.</li>
<li>Handoff validates against schema.</li>
<li>Handoff includes verification status.</li>
<li>Handoff can be loaded into a future case file.</li>
</ol>

## Feature 6: Memory store interface

**Purpose:** Separate the runtime from the memory backend.

<div className="craik-grid">

<div>
<h4><code>EphemeralMemoryStore</code></h4>
<p>For tests and demos. Resets between calls.</p>
</div>

<div>
<h4><code>LocalMemoryStore</code></h4>
<p>SQLite-backed local proposals and approved facts. Persists between CLI calls.</p>
</div>

<div>
<h4><code>StigmemMemoryStore</code></h4>
<p>The reference team-scale substrate. Reads facts, captures provenance, detects optional capabilities.</p>
</div>

</div>

**Required methods:** `search_facts(query, scope)` · `list_facts(entity, relation)` · `propose_fact(proposal)` · `write_fact(fact)` · `invalidate_fact(fact_id, reason)` · `diff(run_id)`.

<ol className="craik-steps">
<li>All backends implement the same interface.</li>
<li>Tests run against the ephemeral backend.</li>
<li>The local backend persists between CLI calls.</li>
<li>The Stigmem backend reads and writes facts with provenance.</li>
<li>The Stigmem backend detects optional recall and conflict capabilities.</li>
<li>Direct Stigmem writes require grants.</li>
<li>Unavailable optional Stigmem capabilities fall back to local Craik state.</li>
</ol>

## Feature 7: GitHub adapter

**Purpose:** Connect Craik tasks to live collaboration state.

<div className="craik-decision">

<div>
<h4>MVP reads</h4>
<ul>
<li>Repository metadata</li>
<li>Open issues</li>
<li>Open PRs</li>
<li>Branch status</li>
<li>Changed files</li>
<li>Comments</li>
<li>CI / check status</li>
</ul>
</div>

<div>
<h4>MVP writes</h4>
<ul>
<li>Create issue</li>
<li>Create PR</li>
<li>Create comment</li>
</ul>
</div>

</div>

<ol className="craik-steps">
<li>GitHub writes require capability grants.</li>
<li>Reads fail gracefully when unauthenticated.</li>
<li>PR / issue references are included in case files.</li>
<li>Created links appear in handoffs.</li>
</ol>

## Feature 8: Work graph

**Purpose:** Model agent work as connected state.

**MVP nodes:** task · handoff · fact · file · issue · PR · receipt · verification.

**MVP edges:** `created_by` · `depends_on` · `verified_by` · `updates` · `blocks` · `contradicts`.

<ol className="craik-steps">
<li>Every task creates a task node.</li>
<li>Every handoff links to the task and its receipts.</li>
<li>Memory proposals link to evidence.</li>
<li>The graph can be exported as JSON.</li>
</ol>

## Feature 9: Contradiction inbox

**Purpose:** Make disagreement operational.

**MVP behavior:** detect contradictions reported by agents · store
contradiction reports · list open contradictions · resolve with
rationale · create memory proposals from resolution.

<ol className="craik-steps">
<li>Contradictions are not silently overwritten.</li>
<li>Resolution records evidence.</li>
<li>Affected artifacts can be listed.</li>
<li>Resolved contradictions appear in the memory diff.</li>
</ol>

## Feature 10: Memory diff

**Purpose:** Explain how memory changed during a run.

**MVP behavior:** list proposed facts · list written facts · list
invalidated facts · list contradictions opened/resolved · list handoff
facts created.

<ol className="craik-steps">
<li>Memory diff can be printed for any task.</li>
<li>Diff is linked from the handoff.</li>
<li>Diff can be stored as a receipt artifact.</li>
</ol>

## Feature 10a: Single-agent execution loop

**Purpose:** Drive one agent through a governed task loop while
preserving state, policy checks, receipts, and stop conditions.

**MVP behavior:** persistent run id · plan → act → observe → evaluate →
continue → stop phases · runner invoked through a step contract · bounded
runner context from defaults + overrides · max-iteration, timeout, and
budget enforcement · policy check before side effects · receipts for
important steps · captured outputs · stop on intent-lock conditions ·
handoffs on completion / block / failure / interruption · resumable
runs.

<ol className="craik-steps">
<li>Craik owns the loop boundary — never an untracked chat transcript.</li>
<li>Loop state is inspectable.</li>
<li>Runner context avoids generated and dependency-path pollution by default.</li>
<li>Context defaults are overridable and their effects are inspectable.</li>
<li>Side effects cannot bypass grants.</li>
<li>Blocked approvals halt the loop.</li>
<li>Memory updates are proposed unless direct writes are granted.</li>
<li>Run recovery does not require replaying raw conversation history.</li>
</ol>

## Feature 11: Orchestrator and specialists

**Purpose:** Support multi-agent workflows after the single-agent loop
works.

**MVP roles:** orchestrator · researcher · docs reviewer · implementer
· verifier · adjudicator.

**Behavior:** orchestrator decomposes the task into child tasks ·
specialists receive case-file excerpts · specialists return typed
worker results · orchestrator merges results into the handoff ·
contradictions are escalated instead of flattened.

<ol className="craik-steps">
<li>Independent read-only tasks can run in parallel.</li>
<li>Worker outputs validate against schema.</li>
<li>Child handoffs link to the parent task.</li>
<li>The orchestrator cannot discard unresolved contradictions.</li>
</ol>

## Feature 11a: First-class runner adapters

**Purpose:** Let Craik work directly with real agent runners instead of
requiring a separate agent framework as the execution layer.

**Initial adapters:** Codex · Claude · Gemini.

**Adapter responsibilities:** receive task request, case file, policy
envelope, and grants · start or guide a runner session · preserve
runner identity and version metadata · capture typed worker results ·
capture receipts or receipt inputs · capture handoff output · return
proposed memory updates · report blocks, failures, or missing
capabilities.

<ol className="craik-steps">
<li>Each adapter implements the same runner interface.</li>
<li>Adapter outputs validate against Craik contracts.</li>
<li>Runner-specific details do not leak into core contracts.</li>
<li>Unsupported capabilities fail clearly.</li>
<li>A task can be replayed or inspected from Craik artifacts without raw chat history.</li>
</ol>

Adjacent-runtime integration is tracked as a later bridge, not a
dependency for this feature.

## Feature 12: Skills and plugins

**Purpose:** Make repeated workflows reusable while keeping authority
governed.

**MVP behavior:** skills are instruction packages scoped to project or
runtime · plugins expose typed capabilities · plugin capabilities
require grants · plugin actions produce receipts · probationary plugins
have restricted permissions · plugins cannot bypass runner or task
policy envelopes.

<ol className="craik-steps">
<li>Project-scoped skills override global skills.</li>
<li>Skills can declare required context contracts.</li>
<li>Plugin descriptors validate.</li>
<li>Probationary plugin use is visible in receipts.</li>
</ol>

## Feature 13: Context contracts

**Purpose:** Define what context a task type must receive.

<div className="craik-grid">

<div>
<h4>Docs review</h4>
<p>docs paths · implementation references · ADR policy · recent facts · stale-risk list.</p>
</div>

<div>
<h4>Implementation</h4>
<p>branch state · test commands · capability grants · relevant issues · coding conventions.</p>
</div>

<div>
<h4>Release work</h4>
<p>version policy · changelog policy · package-registry state · CI requirements.</p>
</div>

</div>

<ol className="craik-steps">
<li>Missing required context blocks execution or creates a warning.</li>
<li>The case file marks satisfied and missing context.</li>
<li>Roles can declare required context contracts.</li>
</ol>

## Feature 14: Agent reputation

**Purpose:** Measure reliability without turning it into popularity.

**Signals:** facts later contradicted · tests passed/failed after edits
· policy violations · handoff completeness · review findings accepted
· tasks completed without rework.

<ol className="craik-steps">
<li>Reputation is scoped by role/domain.</li>
<li>Metrics are explainable.</li>
<li>Reputation affects routing only when policy enables it.</li>
</ol>

<div className="craik-keypoint">

**Scope today**

This feature is not in the MVP implementation. Contracts leave room
for it; the routing surface remains policy-driven.

</div>

## Feature 15: Evidence and assumption management

**Purpose:** Distinguish evidence-backed facts from unverified
assumptions.

**MVP behavior:** case files include evidence references · agent
conclusions can be marked as assumptions · assumptions include
confidence and verification requirements · memory proposals require
evidence references before promotion · handoffs list unresolved
assumptions.

<ol className="craik-steps">
<li>Unsupported assertions do not become direct memory writes.</li>
<li>Assumptions are visible in case files and handoffs.</li>
<li>Evidence references can point to files, commands, GitHub objects, Stigmem facts, user instructions, or prior handoffs.</li>
<li>Memory promotion fails when required evidence is missing.</li>
</ol>

## Feature 16: Agent-native onboarding

**Purpose:** Give a new agent a safe, current project model before it
starts work.

**Target command:** `craik onboard --project <project-id>`

**MVP output:** current project model · active policy profile ·
relevant ADRs and immutable paths · docs boundaries · recent handoffs ·
unresolved contradictions · stale-risk warnings · validation commands ·
Stigmem backend status · allowed next actions.

<ol className="craik-steps">
<li>Onboarding output is generated from the same case-file primitives as tasks.</li>
<li>Stale or missing context is clearly marked.</li>
<li>Policies and write boundaries are visible.</li>
<li>Output is usable by Codex, Claude, and Gemini runner adapters.</li>
</ol>

## Feature 17: Policy tests

**Purpose:** Make runtime policy behavior testable and regressions
visible.

**Required policy tests:** ADR paths cannot be edited in strict mode ·
memory writes become proposals by default · trusted-local fail-open
still records receipts · automation mode fails closed · runner
adapters cannot bypass grants · secrets are redacted from receipts,
logs, handoffs, and case files.

<ol className="craik-steps">
<li>Policy tests run in CI once implementation begins.</li>
<li>Failures identify the violated policy.</li>
<li>Every new policy profile must include fixture tests.</li>
</ol>

## Feature 18: Human delegation points

**Purpose:** Make human approval and clarification part of the work
graph.

**Delegation point types:** approval request · clarification request ·
policy override request · contradiction adjudication request · memory
promotion request · release signoff request.

<ol className="craik-steps">
<li>Delegation points are graph nodes.</li>
<li>Resolution creates receipts.</li>
<li>Unresolved delegation points appear in handoffs.</li>
<li>Agents cannot silently continue past required approvals.</li>
</ol>

## Feature 19: Budget and quota controls

**Purpose:** Keep agent work operationally bounded.

**Budget types:** context tokens · model spend · wall-clock time ·
shell command count · GitHub write count · memory write count ·
parallel worker count · retry count · human approval count.

<ol className="craik-steps">
<li>Budgets can be set by policy profile.</li>
<li>Budget state appears in case files and receipts.</li>
<li>Budget exhaustion blocks or escalates according to policy.</li>
<li>Fail-open profiles do not bypass budget receipts.</li>
</ol>

## Feature 20: Runtime instruction distillation

**Purpose:** Convert declared agent-runtime instruction files into
structured, scoped, provenance-linked runtime memory.

**Sources may include:** `AGENTS.md` · `CLAUDE.md` · `GEMINI.md` ·
`HERMES.md` · `SKILLS.md` · `.cursorrules` ·
`.github/copilot-instructions.md` · `.codex/instructions.md` ·
declared project policy docs.

<ol className="craik-steps">
<li>Declared sources only.</li>
<li>Source path, hash, timestamp, scope, and line/range provenance are tracked.</li>
<li>Extracted items become proposals by default.</li>
<li>Policy constraints can be promoted by approval.</li>
<li>Contradictions between instruction sources are surfaced.</li>
<li>Stale distillations are invalidated when source hashes change.</li>
<li>Case files cite both the distilled item and its source file.</li>
</ol>

## Feature 21: Intent, scratchpad, and scope control

**Purpose:** Keep agent work aligned while allowing temporary thinking.

**Capabilities:** task intent lock · scratchpad with expiry ·
scope-change proposal · first-class unknowns · structured context
requests · context-debt tracking.

<ol className="craik-steps">
<li>Task execution references the accepted intent lock.</li>
<li>Scratchpad entries expire unless promoted.</li>
<li>Out-of-scope discoveries create scope-change proposals.</li>
<li>Unknowns identify what is needed to resolve them.</li>
<li>Context requests are recorded.</li>
<li>Context debt appears in handoffs.</li>
</ol>

## Feature 22: Runtime quality gates

**Purpose:** Improve output quality before durable handoff or memory
writes.

**Capabilities:** self-audit before handoff · runtime critic · red team
mode · handoff quality score · evidence coverage score · tool result
attestation · agent exit discipline.

<ol className="craik-steps">
<li>Major handoffs include self-audit results.</li>
<li>Critic findings are typed and actionable.</li>
<li>High-risk tasks can require red-team review.</li>
<li>Test / command claims distinguish runtime-observed from agent-reported.</li>
<li>Incomplete runs still produce useful exit handoffs.</li>
<li>Low-quality handoffs can block memory promotion.</li>
</ol>

## Feature 23: Runtime intelligence and routing

**Purpose:** Make Craik smarter about runners, evidence, artifacts, and
continuity.

**Capabilities:** runner capability matrix · agent workload memory ·
known traps · evidence expiration rules · knowledge freshness probe ·
policy-aware prompt compiler · real-runner contract tests · work
product classification · "what changed since last time" deltas.

<ol className="craik-steps">
<li>Runner selection can account for capabilities and workload memory.</li>
<li>Known traps appear in onboarding and case files.</li>
<li>Stale evidence can trigger freshness probes.</li>
<li>Prompts compile from shared contracts into runner-specific forms.</li>
<li>Adapter contract tests run against fixture tasks.</li>
<li>Artifacts carry class and lifecycle metadata.</li>
<li>Task start can show relevant deltas since prior runs.</li>
</ol>

## What's next

<div className="craik-next">

<a href="../architecture/">
<strong>Read next</strong>
<span>Architecture</span>
<small>The seven runtime layers these features compose against.</small>
</a>

<a href="../runtime-contracts/">
<strong>Reference</strong>
<span>Runtime contracts</span>
<small>The typed objects every feature speaks.</small>
</a>

<a href="../mvp/">
<strong>Read</strong>
<span>MVP plan</span>
<small>Which of these features ship in the first robust release.</small>
</a>

</div>
