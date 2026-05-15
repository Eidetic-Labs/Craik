# Differentiators

Craik should not become a generic agent launcher. Its differentiators should center on durable, governed, evidence-backed agent work.

This document captures the features that should keep the roadmap from collapsing into basic CLI, storage, and adapter work.

## Evidence-First Execution

Every durable conclusion should be traceable to evidence.

Evidence sources include:

- file reads,
- command output,
- GitHub issues, PRs, comments, and checks,
- Stigmem facts,
- user instructions,
- web sources,
- prior handoffs,
- generated artifacts,
- and runner outputs.

Runtime rule:

> No durable assertion without evidence.

Craik may allow low-confidence assumptions, but they must not be promoted to durable facts without evidence.

## Assumption Ledger

Agents make assumptions constantly. Craik should separate assumptions from facts.

Assumptions should capture:

- statement,
- source,
- confidence,
- task context,
- verification requirement,
- expiration or stale-risk,
- and whether action is allowed before verification.

Assumptions should be visible in case files, handoffs, and memory diffs.

## Belief Promotion Workflow

Craik should distinguish raw agent output from organizational truth.

Recommended lifecycle:

```text
observed -> proposed -> accepted -> relied_upon -> stale -> invalidated
```

This lifecycle should apply to memory proposals and eventually to selected Stigmem facts through metadata or companion facts.

## Context Budgeting As Policy

Context assembly should be explainable.

Case files should capture:

- why each fact, doc, or artifact was included,
- what was summarized,
- what was excluded,
- what was omitted due to budget,
- what must be fetched on demand,
- and whether omitted context creates risk.

## Agent Run Reproducibility

Craik should preserve enough state to understand what an agent knew and what it was allowed to do.

Run records should link:

- task request,
- case file,
- policy envelope,
- runner adapter,
- runner/model metadata,
- capability grants,
- relevant facts,
- receipts,
- commands,
- outputs,
- memory proposals,
- contradictions,
- and handoff.

This is operational replay, not deterministic model replay.

## Trust Boundaries Between Agents

Codex, Claude, Gemini, and future runners should not be treated as equally trusted by default.

Policy should be able to control whether a runner can:

- propose facts,
- write facts,
- edit files,
- run shell commands,
- open GitHub issues or PRs,
- approve another agent's work,
- resolve contradictions,
- or use fail-open profiles.

## Cross-Agent Review Protocol

Craik should define explicit review relationships instead of relying only on orchestrator/specialist decomposition.

Useful roles:

- implementer,
- verifier,
- adversarial reviewer,
- policy reviewer,
- documentation reviewer,
- memory curator,
- release reviewer,
- and adjudicator.

Review outputs should be typed, evidence-linked, and graph-connected.

## Staleness As A First-Class Signal

Old truths are a major failure mode.

Craik should surface staleness for:

- facts,
- docs,
- handoffs,
- assumptions,
- GitHub issue state,
- branch state,
- runner outputs,
- generated artifacts,
- and project policies.

Every case file should be able to say what information is fresh, stale, or unknown.

## Decision Record Suggestions

Craik should notice when runtime knowledge is becoming durable project policy.

Signals:

- repeated reliance on the same fact,
- resolved contradictions that affect future behavior,
- recurring policy overrides,
- repeated documentation updates from the same root cause,
- cross-agent agreement on an architectural constraint.

Craik should not automatically write ADRs. It should suggest that maintainers create or update appropriate decision records when runtime evidence shows a decision has become durable.

## Agent-Native Onboarding

Craik should make onboarding a new agent fast and safe.

Target command:

```text
craik onboard --project <project-id>
```

Output should include:

- current project model,
- active policies,
- relevant ADRs,
- docs boundaries,
- recent handoffs,
- unresolved contradictions,
- validation commands,
- Stigmem connection status,
- known traps,
- and allowed next actions.

## Provenance-Aware Documentation

Craik should help keep documentation tied to the evidence that justified it.

For generated or updated docs, Craik should be able to record:

- source facts,
- source files,
- source issues/PRs,
- relevant policies,
- validation commands,
- authoring agent,
- review agent,
- and update timestamp.

## Policy Tests

Craik policies should be testable.

Examples:

- ADR paths cannot be edited in strict mode.
- Memory writes become proposals by default.
- Trusted-local fail-open still records receipts.
- Automation mode fails closed.
- Runner adapters cannot bypass grants.
- Secrets are redacted from receipts and handoffs.

Policy tests should run in CI and fixture-based local tests.

## Human Delegation Points

Craik should treat human involvement as a runtime primitive, not an interruption.

Agents should be able to create structured delegation points:

- approval request,
- clarification request,
- policy override request,
- contradiction adjudication request,
- memory promotion request,
- release signoff request.

Delegation points should be graph nodes, appear in handoffs, and produce receipts when resolved.

## Budget And Quota Controls

Craik should support policy-level budgets.

Budgets may include:

- context tokens,
- model spend,
- wall-clock time,
- shell command count,
- GitHub write count,
- memory write count,
- parallel worker count,
- retry count,
- and human approval count.

Budgets should be visible in case files and receipts so agent work has operational bounds.

## Learning Without Self-Trust

Craik should improve from agent work without automatically trusting agent-generated conclusions.

Agents may propose:

- facts,
- skills,
- policy refinements,
- validation commands,
- docs updates,
- decision record suggestions,
- and plugin ideas.

But promotion requires evidence, policy, review, or explicit approval.

This principle should guide every self-improving feature:

> Craik may learn continuously, but it should not self-certify truth.

## Runtime Instruction Distillation

Craik should turn declared agent-runtime instruction files into structured runtime memory.

Examples:

- `AGENTS.md`,
- `CLAUDE.md`,
- `GEMINI.md`,
- `HERMES.md`,
- `SKILLS.md`,
- `.cursorrules`,
- `.github/copilot-instructions.md`,
- `.codex/instructions.md`,
- and project policy docs explicitly listed in the project profile.

The source Markdown remains canonical. Distilled output is a provenance-linked runtime projection.

Distilled categories:

- instruction,
- policy,
- preference,
- command,
- boundary,
- handoff rule,
- memory rule,
- security rule,
- stale-risk.

Distillations should track source path, source hash, line/range where available, scope, timestamp, and extraction confidence. Extracted items should become proposals by default and should be invalidated or refreshed when the source hash changes.

## Task Intent Lock

Craik should freeze the accepted task intent before execution.

It should capture:

- original request,
- accepted interpretation,
- excluded work,
- allowed autonomy,
- stop conditions,
- and scope-change rules.

This gives agents a stable north star and makes scope drift reviewable.

## Scratchpad With Expiry

Agents need working memory that is not durable truth.

Craik should provide scratchpad space for:

- temporary notes,
- candidate hypotheses,
- partial findings,
- links to inspect,
- and unresolved fragments.

Scratchpad entries should expire at task end unless promoted to assumptions, facts, handoffs, or artifacts.

## Negative Knowledge

Craik should preserve useful dead ends.

Examples:

- approaches already rejected,
- commands that failed and why,
- APIs that do not exist,
- files inspected and found irrelevant,
- assumptions disproven,
- and package/registry names checked and unavailable.

Negative knowledge should have freshness rules because absence can change.

## Capability Dry Run

Before granting side-effecting capabilities, Craik should let an agent preview intended actions.

The preview may include:

- files expected to change,
- shell commands expected to run,
- GitHub writes expected,
- facts expected to be proposed or written,
- policy triggers,
- and approvals likely needed.

The runtime can then grant narrower authority.

## Evidence Coverage Score

Craik should show whether conclusions are well-supported.

This should not be a fake certainty score. It should indicate evidence coverage:

- unsupported,
- single-source,
- multi-source,
- runtime-observed,
- policy-backed,
- verified by command/test,
- reviewed by another agent or human.

## Structured Agent Debate

When agents disagree, Craik should structure the disagreement.

Debate records should capture:

- claim,
- evidence,
- counterclaim,
- counter-evidence,
- missing verification,
- adjudicator decision,
- and resulting memory updates.

## Self-Audit Before Handoff

Before finishing, agents should run a standard self-audit.

Checklist:

- answered the locked intent,
- stayed in scope,
- cited evidence,
- recorded assumptions,
- recorded validation,
- created needed facts or proposals,
- avoided forbidden paths,
- left next steps,
- and produced a useful handoff.

## Context Debt Tracking

When context is omitted, summarized, or deferred because of budget, Craik should track that as context debt.

Context debt should capture:

- omitted item,
- reason,
- risk,
- required follow-up,
- and whether the current task may proceed.

## Tool Result Attestation

Craik should distinguish how tool results are known.

Result source classes:

- runtime-observed,
- agent-reported,
- user-reported,
- external API result,
- inferred from artifact.

Important claims like "tests passed" should require runtime-observed receipts when possible.

## Runtime Memory Hygiene

Craik should include curator workflows for memory quality.

Curator tasks should find:

- stale assumptions,
- duplicate facts,
- unpromoted useful proposals,
- weak-evidence facts,
- contradictions,
- expired handoffs,
- and obsolete negative knowledge.

Cleanup should be proposed, not automatically destructive by default.

## Recovery Mode

Interrupted runs should be resumable.

Recovery should use:

- task request,
- intent lock,
- case file,
- policy envelope,
- partial receipts,
- scratchpad,
- changed files,
- unfinished handoff,
- unresolved delegations,
- and memory proposals.

Incomplete runs should still leave useful handoffs.

## Runner Capability Matrix

Craik should know what each runner can do.

Capabilities may include:

- shell access,
- file patching,
- browser/web access,
- MCP support,
- image input,
- structured output,
- long context,
- background tasks,
- approval flow,
- and tool-call reliability.

The matrix should influence runner selection, prompt compilation, and policy grants.

## Scope Change Protocol

When an agent finds work outside the locked intent, it should create a scope-change proposal.

The proposal should include:

- requested scope change,
- rationale,
- evidence,
- risk,
- whether current work is blocked,
- and recommended action.

## Knowledge Freshness Probe

Before relying on stale or high-impact facts, Craik should be able to refresh relevant state.

Probe targets:

- repo state,
- GitHub state,
- package registries,
- Stigmem facts,
- local command output,
- and web sources when allowed.

## Public/Internal Boundary Classifier

Craik should classify where content belongs.

Targets:

- public docs,
- internal docs,
- issue or PR comments,
- memory facts,
- handoffs,
- release notes,
- and audit artifacts.

This should be policy-driven and should help prevent internal-only labels or implementation tracking details from leaking into public docs.

## Runtime Context Explanations

Every case-file item should be explainable.

Examples:

- included because policy requires it,
- included because a recent handoff referenced it,
- included because it contradicts a current assumption,
- included because it is stale but high-risk,
- included because the task type requires it.

Agents should be able to ask, "Why am I seeing this?"

## Structured Context Requests

Agents should be able to request more context through a structured protocol.

Example fields:

- need,
- reason,
- urgency,
- allowed source scope,
- blocking status,
- and expected output shape.

Craik should fulfill requests through safe channels and record the result.

## First-Class Unknowns

Agents should be able to say "unknown" without being treated as incomplete.

Unknowns should identify whether resolution requires:

- web access,
- user input,
- repo inspection,
- privileged tool use,
- Stigmem query,
- or waiting for external state.

## Runtime Critic

Craik should support a structured critic pass before accepting major outputs.

The critic should check:

- unsupported claims,
- policy violations,
- scope drift,
- missing validation,
- stale evidence,
- missing handoff,
- unredacted sensitive content,
- and risky memory writes.

## Agent Workload Memory

Craik should remember which agents and runners perform well on which work.

This is routing memory, not social reputation.

Signals:

- strong at docs reconciliation,
- weak at shell-heavy debugging,
- strong at policy review,
- tends to miss stale GitHub state,
- needs stricter context,
- produces high-quality handoffs.

## Known Traps

Projects should maintain known traps.

Examples:

- do not edit ADRs,
- public docs cannot mention internal tracking labels,
- tests must run outside sandbox,
- generated docs live elsewhere,
- local node advertises a different internal port,
- package version is intentionally pre-release.

Known traps should appear in onboarding and case files.

## Evidence Expiration Rules

Evidence should have freshness expectations by source type.

Examples:

- GitHub branch state expires quickly,
- package registry availability changes quickly,
- ADR policy is long-lived,
- command output is tied to worktree and commit,
- web search is time-sensitive,
- user instruction remains active until superseded.

## Handoff Quality Score

Handoffs should be checked for completeness.

Signals:

- completed work,
- changed files,
- validation,
- assumptions,
- unresolved questions,
- next steps,
- facts proposed or written,
- receipts,
- context debt,
- and delegation status.

## Policy-Aware Prompt Compiler

Craik should compile runner-specific prompts from the same underlying runtime contracts.

Inputs:

- locked task intent,
- policy envelope,
- context contract,
- runner capabilities,
- evidence,
- assumptions,
- allowed tools,
- output schema.

Codex, Claude, and Gemini may need different prompt shapes, but the underlying truth should be shared.

## Real-Runner Contract Tests

Mocks are not enough for runner adapters.

Craik should periodically test Codex, Claude, and Gemini adapters against fixture tasks and verify that outputs conform to Craik contracts.

## Memory Impact Preview

Before writing facts to Stigmem, Craik should show a memory diff preview.

Preview should include:

- facts to add,
- facts to invalidate,
- contradictions likely to open,
- affected case files, handoffs, or docs,
- scope and visibility,
- confidence,
- and evidence.

## Agent Exit Discipline

Agents that cannot complete a task should still leave useful state.

Incomplete exits should include:

- why blocked,
- what was checked,
- what is safe to continue,
- what is unsafe,
- missing context,
- unresolved delegations,
- and next best action.

## Red Team Mode

High-risk tasks should support a stricter reviewer mode.

Checks:

- leaked secrets,
- public/internal boundary violations,
- unsupported claims,
- unsafe command grants,
- bad memory writes,
- policy bypasses,
- misleading docs updates.

## Work Product Classification

Every artifact should have a type and lifecycle.

Types:

- scratch,
- proposal,
- implementation,
- review,
- decision,
- release,
- public documentation,
- internal documentation,
- memory update,
- audit artifact.

Artifact class should drive policy.

## What Changed Since Last Time

Before an agent starts, Craik should show relevant deltas since the last related run.

Examples:

- files changed,
- facts changed,
- issues changed,
- PRs changed,
- policies changed,
- handoffs added,
- contradictions opened or resolved,
- package versions changed.

This gives agents continuity without forcing them to rediscover state.
