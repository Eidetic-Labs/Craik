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
