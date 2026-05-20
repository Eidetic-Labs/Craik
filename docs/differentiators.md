# Differentiators

<p className="craik-meta"><span>10 min read</span><span>For engineers &amp; reviewers</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- The features that keep Craik's roadmap from collapsing into basic CLI,
  storage, and adapter work.
- Why every durable assertion must be traceable to evidence.
- How Craik separates raw agent output from organizational truth.
- The runtime primitives — assumption ledger, scope locks, scratchpad
  expiry, context debt, runtime critic — that make agent work auditable.

</div>

<div className="craik-keypoint">

**Don't become a generic agent launcher.**

Craik's differentiators center on durable, governed, evidence-backed
agent work. This doc captures the features that should keep the roadmap
honest as it grows.

</div>

## Evidence-first execution

Every durable conclusion should be traceable to evidence.

<div className="craik-keypoint">

**Runtime rule:** No durable assertion without evidence. Craik may
allow low-confidence assumptions, but they must not be promoted to
durable facts without evidence.

</div>

**Evidence sources:** file reads · command output · GitHub issues, PRs, comments, checks · Stigmem facts · user instructions · web sources · prior handoffs · generated artifacts · runner outputs.

## Assumption ledger

Agents make assumptions constantly. Craik should separate assumptions
from facts. Each assumption captures **statement · source · confidence ·
task context · verification requirement · expiration · whether action
is allowed before verification.** Assumptions are visible in case
files, handoffs, and memory diffs.

## Belief promotion workflow

Craik should distinguish raw agent output from organizational truth.

```text
observed → proposed → accepted → relied_upon → stale → invalidated
```

The lifecycle applies to memory proposals and eventually to selected
Stigmem facts through metadata or companion facts.

## Context budgeting as policy

Context assembly should be explainable. Case files capture **why each
item was included · what was summarized · what was excluded · what was
omitted due to budget · what must be fetched on demand · whether
omissions create risk.**

## Agent run reproducibility

Run records link the full provenance chain so reviewers can replay
operationally — not deterministically — what an agent knew and what it
was allowed to do.

<div className="craik-fields">

<div>
<dt>Linked record</dt>
<dt><span className="craik-fields__type">Purpose</span></dt>
<dd>Why it matters</dd>
</div>

<div>
<dt>task_request</dt>
<dt><span className="craik-fields__type">input</span></dt>
<dd>Original ask the run was launched against.</dd>
</div>

<div>
<dt>case_file</dt>
<dt><span className="craik-fields__type">brief</span></dt>
<dd>Pre-run context bundle.</dd>
</div>

<div>
<dt>policy_envelope</dt>
<dt><span className="craik-fields__type">authority</span></dt>
<dd>What the run was allowed to do.</dd>
</div>

<div>
<dt>runner_adapter + metadata</dt>
<dt><span className="craik-fields__type">execution</span></dt>
<dd>Which runner produced output, with model identifiers.</dd>
</div>

<div>
<dt>capability_grants</dt>
<dt><span className="craik-fields__type">authority</span></dt>
<dd>Explicit permissions exercised.</dd>
</div>

<div>
<dt>relevant_facts</dt>
<dt><span className="craik-fields__type">context</span></dt>
<dd>Memory facts loaded into the case file.</dd>
</div>

<div>
<dt>receipts</dt>
<dt><span className="craik-fields__type">accountability</span></dt>
<dd>Every governed action that fired.</dd>
</div>

<div>
<dt>commands + outputs</dt>
<dt><span className="craik-fields__type">execution</span></dt>
<dd>What ran and what came back, redacted.</dd>
</div>

<div>
<dt>memory_proposals</dt>
<dt><span className="craik-fields__type">delta</span></dt>
<dd>Reviewable facts the run wants to land.</dd>
</div>

<div>
<dt>contradictions</dt>
<dt><span className="craik-fields__type">delta</span></dt>
<dd>Conflicts surfaced during the run.</dd>
</div>

<div>
<dt>handoff</dt>
<dt><span className="craik-fields__type">closure</span></dt>
<dd>The terminal continuity record.</dd>
</div>

</div>

## Trust boundaries between agents

Codex, Claude, Gemini, and future runners are not equally trusted by
default. Policy controls whether a runner may **propose facts · write
facts · edit files · run shell · open issues or PRs · approve another
agent's work · resolve contradictions · use fail-open profiles.**

## Cross-agent review protocol

Explicit review roles instead of single orchestrator/specialist
decomposition.

<div className="craik-grid">

<div><h4>Implementer</h4><p>Does the primary work.</p></div>
<div><h4>Verifier</h4><p>Runs validation, confirms claims.</p></div>
<div><h4>Adversarial reviewer</h4><p>Finds gaps and unsupported claims.</p></div>
<div><h4>Policy reviewer</h4><p>Checks governance compliance.</p></div>
<div><h4>Documentation reviewer</h4><p>Aligns docs with implementation.</p></div>
<div><h4>Memory curator</h4><p>Hygiene over time.</p></div>
<div><h4>Release reviewer</h4><p>Gate before publication.</p></div>
<div><h4>Adjudicator</h4><p>Resolves disagreements.</p></div>

</div>

Review outputs are typed, evidence-linked, and graph-connected.

## Staleness as a first-class signal

Old truths are a major failure mode. Craik surfaces staleness for
**facts · docs · handoffs · assumptions · GitHub issue state · branch
state · runner outputs · generated artifacts · project policies.**
Every case file says what's fresh, stale, or unknown.

## Decision record suggestions

Craik notices when runtime knowledge is becoming durable project policy.

**Signals:** repeated reliance on the same fact · resolved
contradictions that affect future behavior · recurring policy overrides
· repeated docs updates from the same root cause · cross-agent
agreement on an architectural constraint.

Craik **suggests** that maintainers create or update ADRs — it does
not write them automatically.

## Agent-native onboarding

`craik onboard --project <project-id>` outputs the canonical bundle a
new runner needs.

**Output:** current project model · active policies · relevant ADRs ·
docs boundaries · recent handoffs · unresolved contradictions ·
validation commands · Stigmem connection status · known traps ·
allowed next actions.

## Provenance-aware documentation

For generated or updated docs, Craik records **source facts · source
files · source issues/PRs · relevant policies · validation commands ·
authoring agent · review agent · update timestamp.** Documentation
stays tied to the evidence that justified it.

## Policy tests

Craik policies are testable. Policy tests run in CI and fixture-based
local tests.

<div className="craik-grid">

<div><h4>Immutable paths</h4><p>ADRs cannot be edited under strict mode.</p></div>
<div><h4>Memory proposal default</h4><p>Memory writes become proposals unless granted.</p></div>
<div><h4>Trusted-local receipts</h4><p>Fail-open still seals receipts.</p></div>
<div><h4>Automation fail-closed</h4><p>Automation mode stops instead of widening.</p></div>
<div><h4>Grant boundaries</h4><p>Runner adapters cannot bypass grants.</p></div>
<div><h4>Redaction regressions</h4><p>Secrets are scrubbed from receipts and handoffs.</p></div>

</div>

## Human delegation points

Human involvement is a runtime primitive, not an interruption.

**Delegation kinds:** approval request · clarification request · policy
override request · contradiction adjudication request · memory
promotion request · release signoff request.

Delegation points become graph nodes, appear in handoffs, and produce
receipts when resolved.

## Budget and quota controls

Budgets bound agent work with operational limits visible in case files
and receipts: **context tokens · model spend · wall-clock time · shell
command count · GitHub write count · memory write count · parallel
worker count · retry count · human approval count.**

## Learning without self-trust

Agents may propose **facts · skills · policy refinements · validation
commands · docs updates · decision record suggestions · plugin ideas.**
Promotion always requires evidence, policy, review, or explicit
approval.

<div className="craik-keypoint">

**The self-trust rule**

> Craik may learn continuously, but it should not self-certify truth.

This principle guides every self-improving feature.

</div>

## Runtime instruction distillation

Craik turns declared agent-runtime instruction files into structured
runtime memory.

**Recognized sources:** `AGENTS.md` · `CLAUDE.md` · `GEMINI.md` ·
`HERMES.md` · `SKILLS.md` · `.cursorrules` ·
`.github/copilot-instructions.md` · `.codex/instructions.md` ·
project policy docs explicitly listed in the project profile.

Source Markdown remains canonical. Distilled output is a
provenance-linked runtime projection.

**Distilled categories:** instruction · policy · preference · command
· boundary · handoff rule · memory rule · security rule · stale-risk.

Distillations track source path, source hash, line/range, scope,
timestamp, and extraction confidence. Extracted items become proposals
by default and are invalidated when the source hash changes.

## Task intent lock

Craik freezes the accepted task intent before execution. The lock
captures **original request · accepted interpretation · excluded work ·
allowed autonomy · stop conditions · scope-change rules** — giving
agents a stable north star and making scope drift reviewable.

## Scratchpad with expiry

Working memory that is not durable truth. Scratchpad space holds
**temporary notes · candidate hypotheses · partial findings · links to
inspect · unresolved fragments** — and expires at task end unless
promoted to assumptions, facts, handoffs, or artifacts.

## Negative knowledge

Useful dead ends are preserved with freshness rules.

<div className="craik-grid">

<div><h4>Approaches rejected</h4><p>What's already been tried and didn't work.</p></div>
<div><h4>Failed commands</h4><p>Commands that errored and why.</p></div>
<div><h4>Non-existent APIs</h4><p>Endpoints checked and not found.</p></div>
<div><h4>Irrelevant files</h4><p>Files inspected and found unrelated.</p></div>
<div><h4>Disproven assumptions</h4><p>Claims refuted by evidence.</p></div>
<div><h4>Unavailable names</h4><p>Package or registry names checked and not free.</p></div>

</div>

Absence can change — freshness rules apply to negative knowledge too.

## Capability dry run

Before granting side-effecting capabilities, an agent previews intended
actions: **files expected to change · shell commands expected to run ·
GitHub writes expected · facts expected to be proposed or written ·
policy triggers · approvals likely needed.** The runtime then grants
narrower authority.

## Evidence coverage score

A real coverage signal, not a fake certainty score.

<div className="craik-fields">

<div>
<dt>Level</dt>
<dt><span className="craik-fields__type">Source</span></dt>
<dd>What's behind the claim</dd>
</div>

<div>
<dt>unsupported</dt>
<dt><span className="craik-fields__type">none</span></dt>
<dd>No backing source. Always low-confidence.</dd>
</div>

<div>
<dt>single-source</dt>
<dt><span className="craik-fields__type">one citation</span></dt>
<dd>One file/issue/fact. Confidence depends on the source.</dd>
</div>

<div>
<dt>multi-source</dt>
<dt><span className="craik-fields__type">multiple citations</span></dt>
<dd>Multiple independent supports.</dd>
</div>

<div>
<dt>runtime-observed</dt>
<dt><span className="craik-fields__type">live execution</span></dt>
<dd>Output captured at runtime via a wrapper.</dd>
</div>

<div>
<dt>policy-backed</dt>
<dt><span className="craik-fields__type">runtime contract</span></dt>
<dd>The claim is what policy guarantees.</dd>
</div>

<div>
<dt>verified by command/test</dt>
<dt><span className="craik-fields__type">execution result</span></dt>
<dd>A test or command confirms the claim.</dd>
</div>

<div>
<dt>reviewed</dt>
<dt><span className="craik-fields__type">another actor</span></dt>
<dd>Another agent or human reviewed.</dd>
</div>

</div>

## Structured agent debate

When agents disagree, Craik structures the disagreement. Debate records
capture **claim · evidence · counterclaim · counter-evidence · missing
verification · adjudicator decision · resulting memory updates.**

## Self-audit before handoff

Before finishing, agents run a standard self-audit.

<ol className="craik-steps">
<li>Answered the locked intent.</li>
<li>Stayed in scope.</li>
<li>Cited evidence.</li>
<li>Recorded assumptions.</li>
<li>Recorded validation.</li>
<li>Created needed facts or proposals.</li>
<li>Avoided forbidden paths.</li>
<li>Left next steps.</li>
<li>Produced a useful handoff.</li>
</ol>

## Context debt tracking

When context is omitted, summarized, or deferred because of budget,
Craik tracks **omitted item · reason · risk · required follow-up ·
whether the current task may proceed.** Context debt is durable; the
next run inherits it as carryover.

## Tool result attestation

Different result sources have different trust profiles.

<div className="craik-fields">

<div>
<dt>Class</dt>
<dt><span className="craik-fields__type">Trust profile</span></dt>
<dd>When acceptable</dd>
</div>

<div>
<dt>runtime-observed</dt>
<dt><span className="craik-fields__type">high</span></dt>
<dd>Captured by a runtime wrapper; receipted.</dd>
</div>

<div>
<dt>agent-reported</dt>
<dt><span className="craik-fields__type">low</span></dt>
<dd>Agent's claim about a result. Needs verification.</dd>
</div>

<div>
<dt>user-reported</dt>
<dt><span className="craik-fields__type">trust user</span></dt>
<dd>Operator-asserted state.</dd>
</div>

<div>
<dt>external API</dt>
<dt><span className="craik-fields__type">scoped</span></dt>
<dd>Captured from a remote service receipt.</dd>
</div>

<div>
<dt>inferred</dt>
<dt><span className="craik-fields__type">low</span></dt>
<dd>Derived from an artifact, not directly observed.</dd>
</div>

</div>

Important claims like "tests passed" should require runtime-observed
receipts whenever possible.

## Runtime memory hygiene

Curator workflows for memory quality. Curator tasks find **stale
assumptions · duplicate facts · unpromoted useful proposals ·
weak-evidence facts · contradictions · expired handoffs · obsolete
negative knowledge.** Cleanup is proposed, never automatically
destructive by default.

## Recovery mode

Interrupted runs are resumable. Recovery uses **task request · intent
lock · case file · policy envelope · partial receipts · scratchpad ·
changed files · unfinished handoff · unresolved delegations · memory
proposals.** Incomplete runs still leave useful handoffs.

## Runner capability matrix

Craik knows what each runner can do — and routes accordingly.

**Capabilities tracked:** shell access · file patching · browser/web
access · MCP support · image input · structured output · long context ·
background tasks · approval flow · tool-call reliability.

The matrix influences runner selection, prompt compilation, and policy
grants.

## Scope change protocol

When an agent finds work outside the locked intent, it files a
scope-change proposal capturing **requested scope change · rationale ·
evidence · risk · whether current work is blocked · recommended
action.**

## Knowledge freshness probe

Before relying on stale or high-impact facts, Craik can refresh
relevant state.

**Probe targets:** repo state · GitHub state · package registries ·
Stigmem facts · local command output · web sources (when allowed).

## Public / internal boundary classifier

Craik classifies where content belongs and helps prevent internal-only
labels or implementation tracking details from leaking into public
docs.

**Targets:** public docs · internal docs · issue or PR comments ·
memory facts · handoffs · release notes · audit artifacts.

## Runtime context explanations

Every case-file item is explainable. Agents should be able to ask, "Why
am I seeing this?" and get a real answer.

<div className="craik-grid">

<div><h4>Policy required</h4><p>Included because policy mandates it.</p></div>
<div><h4>Recent handoff</h4><p>Included because a recent handoff referenced it.</p></div>
<div><h4>Contradiction</h4><p>Included because it contradicts a current assumption.</p></div>
<div><h4>Stale + high-risk</h4><p>Included because it is stale but high-risk.</p></div>
<div><h4>Task-type</h4><p>Included because the task type requires it.</p></div>

</div>

## Structured context requests

Agents request more context through a structured protocol. Fields:
**need · reason · urgency · allowed source scope · blocking status ·
expected output shape.** Craik fulfills requests through safe channels
and records the result.

## First-class unknowns

Agents say "unknown" without being treated as incomplete. Unknowns
identify whether resolution requires **web access · user input · repo
inspection · privileged tool use · Stigmem query · waiting for external
state.**

## Runtime critic

A structured critic pass before accepting major outputs.

<div className="craik-grid">

<div><h4>Unsupported claims</h4><p>Claims without evidence references.</p></div>
<div><h4>Policy violations</h4><p>Actions that crossed the envelope.</p></div>
<div><h4>Scope drift</h4><p>Work outside the intent lock.</p></div>
<div><h4>Missing validation</h4><p>Claims unverified by command or test.</p></div>
<div><h4>Stale evidence</h4><p>Citations that may have moved.</p></div>
<div><h4>Missing handoff</h4><p>Run that didn't close cleanly.</p></div>
<div><h4>Unredacted content</h4><p>Sensitive data that slipped through.</p></div>
<div><h4>Risky memory writes</h4><p>Promotions without sufficient evidence.</p></div>

</div>

## Agent workload memory

Routing memory, not social reputation. Craik remembers which agents
and runners perform well on which work.

**Signal examples:** strong at docs reconciliation · weak at
shell-heavy debugging · strong at policy review · tends to miss stale
GitHub state · needs stricter context · produces high-quality handoffs.

## Known traps

Projects maintain known traps — negative knowledge appearing in
onboarding and case files.

<div className="craik-grid">

<div><h4>Don't edit ADRs</h4></div>
<div><h4>Public docs can't reference internal labels</h4></div>
<div><h4>Tests must run outside the sandbox</h4></div>
<div><h4>Generated docs live elsewhere</h4></div>
<div><h4>Local node advertises a non-standard port</h4></div>
<div><h4>Package version is intentionally pre-release</h4></div>

</div>

## Evidence expiration rules

Different evidence kinds have different shelf lives.

<div className="craik-fields">

<div>
<dt>Source</dt>
<dt><span className="craik-fields__type">Freshness</span></dt>
<dd>Why</dd>
</div>

<div>
<dt>GitHub branch state</dt>
<dt><span className="craik-fields__type">expires quickly</span></dt>
<dd>Branches advance every push.</dd>
</div>

<div>
<dt>Package registry availability</dt>
<dt><span className="craik-fields__type">expires quickly</span></dt>
<dd>Names can be claimed at any time.</dd>
</div>

<div>
<dt>ADR policy</dt>
<dt><span className="craik-fields__type">long-lived</span></dt>
<dd>Decisions change rarely and explicitly.</dd>
</div>

<div>
<dt>Command output</dt>
<dt><span className="craik-fields__type">tied to commit</span></dt>
<dd>Validity depends on the worktree state.</dd>
</div>

<div>
<dt>Web search</dt>
<dt><span className="craik-fields__type">time-sensitive</span></dt>
<dd>Content can change at any moment.</dd>
</div>

<div>
<dt>User instruction</dt>
<dt><span className="craik-fields__type">until superseded</span></dt>
<dd>Active until the operator updates it.</dd>
</div>

</div>

## Handoff quality score

Handoffs are checked for completeness.

**Signals:** completed work · changed files · validation · assumptions
· unresolved questions · next steps · facts proposed or written ·
receipts · context debt · delegation status.

## Policy-aware prompt compiler

Craik compiles runner-specific prompts from the same underlying
runtime contracts.

**Inputs:** locked task intent · policy envelope · context contract ·
runner capabilities · evidence · assumptions · allowed tools · output
schema.

Codex, Claude, and Gemini may need different prompt shapes, but the
underlying truth is shared.

## Real-runner contract tests

Mocks are not enough for runner adapters. Craik periodically tests
Codex, Claude, and Gemini adapters against fixture tasks and verifies
that outputs conform to Craik contracts.

## Memory impact preview

Before writing facts to Stigmem, Craik shows a memory-diff preview:
**facts to add · facts to invalidate · contradictions likely to open ·
affected case files / handoffs / docs · scope and visibility ·
confidence · evidence.**

## Agent exit discipline

Agents that cannot complete a task still leave useful state.

**Incomplete exits include:** why blocked · what was checked · what is
safe to continue · what is unsafe · missing context · unresolved
delegations · next best action.

## Red team mode

High-risk tasks support a stricter reviewer mode. Checks include
**leaked secrets · public/internal boundary violations · unsupported
claims · unsafe command grants · bad memory writes · policy bypasses ·
misleading docs updates.**

## Work product classification

Every artifact has a type and lifecycle, and the class drives policy.

<div className="craik-grid">

<div><h4>Scratch</h4><p>Expires at task end.</p></div>
<div><h4>Proposal</h4><p>Awaits review.</p></div>
<div><h4>Implementation</h4><p>The primary deliverable.</p></div>
<div><h4>Review</h4><p>Cross-agent review output.</p></div>
<div><h4>Decision</h4><p>ADR or equivalent.</p></div>
<div><h4>Release</h4><p>Versioned, signed.</p></div>
<div><h4>Public docs</h4><p>External-facing.</p></div>
<div><h4>Internal docs</h4><p>Operator-only.</p></div>
<div><h4>Memory update</h4><p>Fact-store delta.</p></div>
<div><h4>Audit artifact</h4><p>Receipt, handoff, graph export.</p></div>

</div>

## What changed since last time

Before an agent starts, Craik shows relevant deltas since the last
related run — continuity without forcing rediscovery.

**Tracked deltas:** files changed · facts changed · issues changed ·
PRs changed · policies changed · handoffs added · contradictions
opened or resolved · package versions changed.

## What's next

<div className="craik-next">

<a href="features.md">
<strong>Read next</strong>
<span>Features</span>
<small>The implementable feature surface — every MVP behavior with acceptance criteria.</small>
</a>

<a href="architecture.md">
<strong>Read</strong>
<span>Architecture</span>
<small>The seven runtime layers that compose these differentiators.</small>
</a>

<a href="concepts/governance.md">
<strong>Concept</strong>
<span>Governance</span>
<small>The runtime contract the differentiators ride on top of.</small>
</a>

</div>
