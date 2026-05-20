# Product Strategy

<p className="craik-meta"><span>6 min read</span><span>For founders &amp; product</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- Why Craik is a *durable agent runtime*, not another framework.
- The agent-runner strategy (Codex / Claude / Gemini as first-class).
- The license rationale and the brand boundary.
- The patterns Craik borrows from local-agent and multi-agent runtimes,
  plus the things Craik adds on top.

</div>

<div className="craik-keypoint">

**A new product category**

The opportunity is to combine approachable local-agent ergonomics,
multi-agent decomposition, and Stigmem's durable memory/truth substrate
into a new product category: a durable runtime for agent organizations.

</div>

Craik should build on strong agent-runtime and multi-agent coordination
patterns without becoming a clone of any adjacent tool.

## Agent runner strategy

Craik should be built for agents to use directly. The initial first-class
runner targets are Codex, Claude, and Gemini — direct adapters that
consume the same Craik contracts.

Craik core stays runner-agnostic through contracts, and the first
implementation ships direct runner adapters that can:

<div className="craik-grid">

<div>
<h4>Receive case files</h4>
<p>Project case file, policy envelope, and capability grants — typed
inputs the adapter normalizes for the runner.</p>
</div>

<div>
<h4>Execute or guide</h4>
<p>Run a fixture-backed task or hand off to a live runner with the same
contracts on the way back.</p>
</div>

<div>
<h4>Emit typed worker results</h4>
<p>Findings, artifacts, assumptions, risks, contradictions — preserved
as <code>craik.worker_result</code>.</p>
</div>

<div>
<h4>Emit receipts &amp; handoffs</h4>
<p>Capability receipts and durable handoffs at the same boundary every
other governed action uses.</p>
</div>

<div>
<h4>Propose memory updates</h4>
<p>Run outputs may create reviewable memory proposals — but never write
durable facts directly.</p>
</div>

</div>

Craik should not depend on another agent framework as its initial
execution layer. Adjacent tools are useful references for local and
self-hosted ergonomics, gateway design, workspace identity, sessions,
tool descriptors, skills, and channel integrations. Craik's first
agent path is direct integration with Codex, Claude, and Gemini.

## License strategy

<div className="craik-keypoint">

**Craik uses the MIT License.**

The code license stays separate from brand and trademark usage. Eidetic
Labs reserves the right to define how the Craik name, marks, and hosted
service branding may be used.

</div>

The license choice supports:

<div className="craik-grid">

<div>
<h4>Low-friction adoption</h4>
<p>Individuals, startups, and enterprises can integrate Craik without
license-review friction.</p>
</div>

<div>
<h4>Permissive norm</h4>
<p>Matches the permissive license norm set by comparable agent projects.</p>
</div>

<div>
<h4>Plugin &amp; adapter growth</h4>
<p>Makes downstream packages easier to ship under their own choice of
license.</p>
</div>

<div>
<h4>Commercial flexibility</h4>
<p>Leaves room for hosted services and enterprise offerings without
changing the runtime license.</p>
</div>

<div>
<h4>Broader distribution</h4>
<p>Permissive licensing helps the runtime concepts travel further as
reference patterns.</p>
</div>

</div>

## Local agent runtime patterns

The strongest local-agent runtime lessons are operational and ergonomic.

<div className="craik-decision">

<div>
<h4>Craik adopts</h4>
<ul>
<li><strong>Self-hosted first</strong> — run locally or on your own infra.</li>
<li><strong>Gateway ergonomics</strong> — one entry point for users, agents, tools, sessions, channels.</li>
<li><strong>Workspace identity</strong> — scoped files, runtime config, persistent session artifacts.</li>
<li><strong>Session continuity</strong> — agent runs survive restarts and stay inspectable.</li>
<li><strong>Skills as operating guidance</strong> — installable, scoped, reusable.</li>
<li><strong>Typed tool descriptors</strong> — tools as explicit capabilities, not hidden prompt affordances.</li>
<li><strong>Channel flexibility</strong> — CLI first, UI/API next, chat surfaces later.</li>
</ul>
</div>

<div>
<h4>Craik adds</h4>
<ul>
<li><strong>Structured case files</strong> instead of broad transcript state.</li>
<li><strong>Capability receipts</strong> for important tool use.</li>
<li><strong>Explicit memory-write policy</strong> — proposal-first by default.</li>
<li><strong>Trust-aware facts</strong> with scope and provenance.</li>
<li><strong>Contradiction workflows</strong> instead of silent overwrites.</li>
<li><strong>Project-level work graphs</strong> connecting tasks, evidence, and decisions.</li>
</ul>
</div>

</div>

Adjacent local runtimes are design references and possible later
integration targets, not core dependencies.

## Multi-agent coordination patterns

The strongest multi-agent lessons are about decomposition, role
separation, and durable coordination.

<div className="craik-decision">

<div>
<h4>Craik adopts</h4>
<ul>
<li><strong>Orchestrator plus specialists</strong> for complex work.</li>
<li><strong>Isolated worker context</strong> — task-relevant only.</li>
<li><strong>Typed result objects</strong> — validated, routable.</li>
<li><strong>Parallel execution</strong> where safe.</li>
<li><strong>Task boards</strong> that outlive a single chat session.</li>
<li><strong>Worker heartbeats and blocks</strong> for progress, blocking, and context requests.</li>
<li><strong>Role profiles</strong> with explicit responsibilities, tools, and policy.</li>
</ul>
</div>

<div>
<h4>Craik adds</h4>
<ul>
<li><strong>Handoffs, not summaries</strong> — workers write durable continuity records.</li>
<li><strong>Work graph linkage</strong> — task boards connect to typed cross-cutting state.</li>
<li><strong>Evidence-bearing outputs</strong> — specialist results become artifacts, not chat.</li>
<li><strong>Tracked contradictions</strong> instead of unresolved disagreement.</li>
<li><strong>Stigmem-backed memory</strong> instead of orchestrator-only memory.</li>
</ul>
</div>

</div>

## What Craik adds

Craik's novel surface is built around features that are difficult to
retrofit into prompt-first systems.

<div className="craik-grid">

<div>
<h4>Project case file</h4>
<p>The task-specific context package assembled before an agent acts —
objective, policy envelope, facts, ADRs, repository and GitHub state,
recent handoffs, stale-risk warnings, contradiction warnings, and
required verification.</p>
</div>

<div>
<h4>Durable handoff</h4>
<p>Machine-readable continuity record — what was done, what changed,
evidence used, commands and tests run, facts learned and invalidated,
unresolved questions, blocked items, risks, and recommended next steps.</p>
</div>

<div>
<h4>Capability receipt</h4>
<p>Concise record of important runtime action — file writes, shell, GitHub
writes, memory writes, PR/issue creation, contradiction events, and
approval grants.</p>
</div>

<div>
<h4>Memory diff</h4>
<p>How project memory changed during a run — facts added, updated,
invalidated; contradictions opened or resolved; stale facts refreshed;
handoffs linked.</p>
</div>

<div>
<h4>Contradiction inbox</h4>
<p>Collects incompatible facts or conclusions with grouping, evidence,
affected artifacts, reviewer assignment, proposed resolution, and the
memory update after resolution.</p>
</div>

<div>
<h4>Work graph</h4>
<p>Turns chat-like agent runs into durable connected work linking tasks,
agents, handoffs, facts, docs, ADRs, branches, issues, PRs, commands,
tests, approvals, and artifacts.</p>
</div>

<div>
<h4>Evidence &amp; assumption management</h4>
<p>Makes it clear what an agent knows, what it assumes, and what
evidence supports each durable assertion — a stronger truth model than
ordinary agent memory.</p>
</div>

<div>
<h4>Agent-native onboarding</h4>
<p>Lets Codex, Claude, Gemini, and future runners join a project with
project model, recent handoffs, policy boundaries, unresolved
contradictions, stale-risk warnings, and allowed next actions.</p>
</div>

<div>
<h4>Policy tests &amp; human delegation</h4>
<p>Policies are testable. Human approval and clarification are modeled
as structured delegation points — not untracked chat interruptions.</p>
</div>

<div>
<h4>Budgets &amp; quotas</h4>
<p>Bounds agent work with policy-level budgets for context, model spend,
time, writes, commands, retries, parallelism, and approvals.</p>
</div>

<div>
<h4>Instruction distillation</h4>
<p>Distills declared instruction files (<code>AGENTS.md</code>,
<code>CLAUDE.md</code>, <code>GEMINI.md</code>, <code>HERMES.md</code>,
<code>SKILLS.md</code>) into structured, scoped, provenance-linked
proposals — never treating raw Markdown as unreviewed truth.</p>
</div>

<div>
<h4>Quality &amp; continuity</h4>
<p>Quality gates, recovery mode, runner-capability awareness, known
traps, freshness probes, work-product classification, and
"what changed since last time" deltas.</p>
</div>

</div>

## Product differentiation

Craik should be described in terms of durable work, not swarm novelty.

<div className="craik-decision">

<div>
<h4>Prefer</h4>
<ul>
<li>Durable agent runtime</li>
<li>Shared project model</li>
<li>Governed multi-agent work</li>
<li>Verifiable handoffs</li>
<li>Capability receipts</li>
<li>Memory-native coordination</li>
</ul>
</div>

<div>
<h4>Avoid</h4>
<ul>
<li>"Agent swarm"</li>
<li>"Autonomous everything"</li>
<li>"One prompt to replace your team"</li>
<li>"Memory chatbot"</li>
</ul>
</div>

</div>

## First audience

The first audience is **small engineering teams using coding agents on
real repositories**. They already feel the pain:

<div className="craik-grid">

<div>
<h4>Agents repeat investigations</h4>
<p>Each session reconstructs context from scratch. No shared model.</p>
</div>

<div>
<h4>Docs lag implementation</h4>
<p>Stale docs become traps. No way to surface "this might be out of date".</p>
</div>

<div>
<h4>Chat context disappears</h4>
<p>Useful state lives only in a transcript that doesn't survive the
session.</p>
</div>

<div>
<h4>Multiple agents step on each other</h4>
<p>No coordination layer; no work graph.</p>
</div>

<div>
<h4>Handoffs are informal</h4>
<p>"Whatever was in the chat" — instead of typed continuity records.</p>
</div>

<div>
<h4>Governance is human discipline</h4>
<p>Policy lives in code review comments, not in the runtime.</p>
</div>

</div>

Craik should make those failures visible, structured, and fixable.

## What's next

<div className="craik-next">

<a href="differentiators.md">
<strong>Read next</strong>
<span>Differentiators</span>
<small>The features that keep the roadmap from collapsing into basic CLI plumbing.</small>
</a>

<a href="features.md">
<strong>Read</strong>
<span>Features</span>
<small>The implementable feature surface — every MVP behavior with acceptance criteria.</small>
</a>

<a href="architecture.md">
<strong>Read</strong>
<span>Architecture</span>
<small>The seven runtime layers and the contracts that hold them together.</small>
</a>

</div>
