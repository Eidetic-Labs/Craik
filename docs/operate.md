---
id: operate
title: Operate
sidebar_label: Overview
sidebar_position: 0
description: Run, monitor, and maintain Craik. Inspect operator views, manage state, and handle long-running concerns.
slug: /operate
---

# Operate Craik

This section is for the people running Craik in anger — daily diagnostics,
release practice, the operator views that surface what's happening inside a
run, and the supporting subsystems (gateway, channels, companion apps,
multimodal, locale).

## Implementation paths

<header className="craik-section-banner">
<div className="craik-section-banner__num" aria-hidden="true">01</div>
<div className="craik-section-banner__body">
<p className="craik-section-banner__kicker">Day-to-day operations</p>
<h3 className="craik-section-banner__title">
The four commands <em>you reach for most often.</em>
</h3>
<p className="craik-section-banner__lede">
Read-only diagnostics, the contributor quality gates, the safe-update
flow, and the release cadence. Start here if you're picking up an
already-running install or preparing to cut a release.
</p>
</div>
</header>

<div className="craik-product-spread">

<a className="craik-product-feature" href="guides/doctor.md">
<div>
<p className="craik-product-feature__num">Diagnostic · 01</p>
<h4 className="craik-product-feature__title">Doctor diagnostics</h4>
<p className="craik-product-feature__summary">
The read-only health check. Inspects local home, SQLite store, memory
backend, every auth profile, gateway config, gateway prerequisites,
and policy state — without contacting Stigmem or writing receipts.
Run it before going live or whenever something feels off.
</p>
<ul className="craik-product-feature__topics">
<li>read-only</li>
<li>auth-profile health</li>
<li>structured statuses</li>
<li>CI-friendly JSON</li>
</ul>
<span className="craik-product-feature__cta">Run doctor</span>
</div>
<blockquote className="craik-product-feature__quote">
<p className="craik-product-feature__quote-eyebrow">Read-only</p>
<p className="craik-product-feature__quote-text">
<code>craik doctor</code> inspects existing local state and environment
variables. It does not create <code>CRAIK_HOME</code>, initialize a
database, contact Stigmem, start a gateway, or write receipts.
</p>
<p className="craik-product-feature__quote-attribution">— Doctor diagnostics · §Read-only</p>
</blockquote>
</a>

</div>

<ol className="craik-adr-grid">

<li>
<a className="craik-adr-card" href="guides/development.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">02</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Quality gates</span>
</div>
<h4 className="craik-adr-card__title">Development checks</h4>
<p className="craik-adr-card__decision">
The four core gates contributors run before opening a PR: pytest,
ruff, mypy, and <code>craik policy test</code>. Same set CI exercises
on every push — green locally usually means green in CI.
</p>
<span className="craik-adr-card__cta">Guide</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="guides/updating.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">03</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Safe update</span>
</div>
<h4 className="craik-adr-card__title">Updating Craik</h4>
<p className="craik-adr-card__decision">
<code>craik update</code> prints safe update guidance only — it does
not modify the installed package, rewrite source checkouts, fetch
remote release metadata, or migrate local state. Operator stays in
control of the actual upgrade.
</p>
<span className="craik-adr-card__cta">Guide</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="guides/release-management.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">04</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Release</span>
</div>
<h4 className="craik-adr-card__title">Release management</h4>
<p className="craik-adr-card__decision">
The release cadence and gates for the <code>0.x.0</code> MVP series.
Each published release must be installable, documented, and
recoverable — contracts can change between minor releases but never
without docs and tests.
</p>
<span className="craik-adr-card__cta">Guide</span>
</a>
</li>

</ol>

<header className="craik-section-banner">
<div className="craik-section-banner__num" aria-hidden="true">02</div>
<div className="craik-section-banner__body">
<p className="craik-section-banner__kicker">Local state &amp; migrations</p>
<h3 className="craik-section-banner__title">
Where state lives — <em>and how to move it.</em>
</h3>
<p className="craik-section-banner__lede">
Four docs cover the on-disk layout, the SQLite local store, the
forward-only migration discipline, and the strict secret-handling
policy that applies whenever data crosses runtime boundaries.
</p>
</div>
</header>

<div className="craik-product-spread">

<a className="craik-product-feature" href="reference/local-store.md">
<div>
<p className="craik-product-feature__num">Persistence · 01</p>
<h4 className="craik-product-feature__title">Local store</h4>
<p className="craik-product-feature__summary">
SQLite at <code>$CRAIK_HOME/state/craik.sqlite3</code>. Holds projects,
tasks, intent locks, case files, run state, receipts, handoffs, memory
proposals, contradictions, and work-graph projections. Schema is
versioned; migrations run on <code>LocalStore.initialize()</code>.
</p>
<ul className="craik-product-feature__topics">
<li>SQLite</li>
<li>versioned schema</li>
<li>forward-only</li>
<li>single source of truth</li>
</ul>
<span className="craik-product-feature__cta">Read the store</span>
</div>
<blockquote className="craik-product-feature__quote">
<p className="craik-product-feature__quote-eyebrow">Persistence</p>
<p className="craik-product-feature__quote-text">
Craik uses SQLite for local runtime persistence.
</p>
<p className="craik-product-feature__quote-attribution">— Local store · §Intro</p>
</blockquote>
</a>

</div>

<ol className="craik-adr-grid">

<li>
<a className="craik-adr-card" href="reference/local-state.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">02</span>
<span className="craik-adr-card__status craik-adr-card__status--type">On-disk layout</span>
</div>
<h4 className="craik-adr-card__title">Local state layout</h4>
<p className="craik-adr-card__decision">
The full <code>~/.craik/</code> directory map: <code>config/</code>,
<code>secrets/</code>, <code>state/</code>, <code>cache/</code>,
<code>logs/</code>, <code>receipts/</code>, <code>handoffs/</code>,
<code>case-files/</code>, <code>projects/</code>. Override the root
with <code>CRAIK_HOME</code>.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="guides/local-store-migrations.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">03</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Migrations</span>
</div>
<h4 className="craik-adr-card__title">Local store migrations</h4>
<p className="craik-adr-card__decision">
Migrations are forward-only and run during
<code>LocalStore.initialize()</code>. Each step is versioned; a
schema-version table tracks what has applied so a re-initialization
is idempotent.
</p>
<span className="craik-adr-card__cta">Guide</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/secret-migration-policy.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">04</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Policy</span>
</div>
<h4 className="craik-adr-card__title">Secret migration policy</h4>
<p className="craik-adr-card__decision">
Migration workflows must never copy secret values across runtime
boundaries. Secret-bearing fields are handled through one of four
policy outcomes — <code>redact</code>, <code>strip</code>,
<code>reference</code>, or <code>reject</code> — never copied as-is.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

</ol>

<header className="craik-section-banner">
<div className="craik-section-banner__num" aria-hidden="true">03</div>
<div className="craik-section-banner__body">
<p className="craik-section-banner__kicker">Operator views</p>
<h3 className="craik-section-banner__title">
Seventeen <em>read-only inspection surfaces.</em>
</h3>
<p className="craik-section-banner__lede">
Every typed runtime record has a matching named view. Work graph,
handoffs, receipts, contradictions, evidence, delegation queues,
budget, quality, run deltas, memory previews, traps, preferences, and
instruction provenance — each surfaces what an operator needs without
mutating state.
</p>
<p className="craik-section-banner__lede">
<strong>Current scope:</strong> Craik ships the typed view contracts
and formatter helpers today. A complete TUI or dashboard is
<a href="../reference/post-mvp-scope/">post-MVP scope</a>.
</p>
</div>
</header>

<div className="craik-product-spread">

<a className="craik-product-feature" href="reference/operator-surface.md">
<div>
<p className="craik-product-feature__num">Catalog · 01</p>
<h4 className="craik-product-feature__title">Operator surface</h4>
<p className="craik-product-feature__summary">
The umbrella catalog. Names every operator view, the records it reads,
and the formatter helpers Craik ships for rendering them. The contracts
are stable enough today that any TUI or dashboard can be built on top
without renegotiating with core.
</p>
<ul className="craik-product-feature__topics">
<li>view contracts</li>
<li>formatter helpers</li>
<li>read-only</li>
<li>dashboard substrate</li>
</ul>
<span className="craik-product-feature__cta">Read the catalog</span>
</div>
<blockquote className="craik-product-feature__quote">
<p className="craik-product-feature__quote-eyebrow">Today</p>
<p className="craik-product-feature__quote-text">
Craik has read-only operator view contracts and formatter helpers. A
complete TUI or dashboard is post-MVP scope.
</p>
<p className="craik-product-feature__quote-attribution">— Operator surface · §Intro</p>
</blockquote>
</a>

</div>

<ol className="craik-adr-grid">

<li>
<a className="craik-adr-card" href="reference/work-graph-explorer.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">02</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · graph</span>
</div>
<h4 className="craik-adr-card__title">Work graph explorer</h4>
<p className="craik-adr-card__decision">
Reads <code>craik.work_graph_export</code> and
<code>craik.work_graph_event</code> records. Renders the connected
state of tasks, case files, handoffs, receipts, memory proposals,
evidence, assumptions, and contradictions.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/handoff-viewer.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">03</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · handoff</span>
</div>
<h4 className="craik-adr-card__title">Handoff viewer</h4>
<p className="craik-adr-card__decision">
Renders one <code>craik.handoff</code> record with its receipts, memory
proposals, assumptions, context debt, and self-audit. The default
surface for picking up a paused or completed run.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/receipt-viewer.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">04</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · receipt</span>
</div>
<h4 className="craik-adr-card__title">Receipt viewer</h4>
<p className="craik-adr-card__decision">
Renders one <code>craik.capability_receipt</code> with operator,
credential, capability, target, reason, result, and the policy
envelope that gated it. Joins back to the task and handoff.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/contradiction-inbox-view.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">05</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · contradiction</span>
</div>
<h4 className="craik-adr-card__title">Contradiction inbox view</h4>
<p className="craik-adr-card__decision">
Read-only view over <code>craik.contradiction_report</code> records.
Surfaces open contradictions with their evidence, owner, proposed
resolution, status, and optional Stigmem conflict id.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/evidence-assumption-view.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">06</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · evidence</span>
</div>
<h4 className="craik-adr-card__title">Evidence &amp; assumption view</h4>
<p className="craik-adr-card__decision">
Renders <code>craik.evidence_reference</code> and
<code>craik.assumption</code> records side by side so a reviewer can
tell what was cited from what was guessed.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/delegation-queue-view.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">07</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · delegation</span>
</div>
<h4 className="craik-adr-card__title">Delegation queue view</h4>
<p className="craik-adr-card__decision">
Read-only view over <code>craik.human_delegation_point</code> records
— the things a run paused on, waiting for a human decision.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/budget-quota-view.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">08</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · budget</span>
</div>
<h4 className="craik-adr-card__title">Budget &amp; quota view</h4>
<p className="craik-adr-card__decision">
Configured limits, observed usage, missing data, exceeded limits, and
operator notes for tokens, time, and credentials.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/quality-gate-view.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">09</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · quality</span>
</div>
<h4 className="craik-adr-card__title">Quality gate view</h4>
<p className="craik-adr-card__decision">
Handoff quality scores, evidence coverage, runtime critic findings,
and red-team outcomes — every quality signal in one operator panel.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/run-delta-view.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">10</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · delta</span>
</div>
<h4 className="craik-adr-card__title">Run delta view</h4>
<p className="craik-adr-card__decision">
Continuity-relevant changes since the previous usable handoff or
resume point. The "what's new since I was last here?" surface.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/memory-impact-preview-view.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">11</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · memory</span>
</div>
<h4 className="craik-adr-card__title">Memory impact preview view</h4>
<p className="craik-adr-card__decision">
Read-only preview of proposed memory writes <em>before</em> promotion
or direct write attempts. Surfaces facts that would be added or
invalidated and likely contradictions.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/memory-review-nudges.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">12</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · memory</span>
</div>
<h4 className="craik-adr-card__title">Memory review nudges</h4>
<p className="craik-adr-card__decision">
Identifies facts that should be reviewed without directly rewriting
memory. Nudges are signals for the reviewer, never autonomous edits.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/known-traps-view.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">13</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · traps</span>
</div>
<h4 className="craik-adr-card__title">Known traps view</h4>
<p className="craik-adr-card__decision">
Surfaces known traps and negative knowledge — what <em>not</em> to do
on this project, with reasons. The institutional memory of failed
approaches.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/preference-facts.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">14</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · preferences</span>
</div>
<h4 className="craik-adr-card__title">Preference facts</h4>
<p className="craik-adr-card__decision">
Models user and team preferences as reviewable records. Preferences
are facts with explicit scope, not implicit settings buried in config.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/instruction-distillation-view.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">15</span>
<span className="craik-adr-card__status craik-adr-card__status--type">View · instructions</span>
</div>
<h4 className="craik-adr-card__title">Instruction distillation view</h4>
<p className="craik-adr-card__decision">
Renders declared instruction sources, observed source snapshots,
provenance, and distilled proposals so a reviewer can see where each
runtime constraint actually came from.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/instruction-distillation-workflow.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">16</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Workflow · instructions</span>
</div>
<h4 className="craik-adr-card__title">Instruction distillation workflow</h4>
<p className="craik-adr-card__decision">
Turns declared instruction files into reviewed, provenance-linked
runtime constraints. Raw instruction files are evidence — never
authority — until distilled through review.
</p>
<span className="craik-adr-card__cta">Workflow</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/instruction-sources.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">17</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Registry · instructions</span>
</div>
<h4 className="craik-adr-card__title">Instruction sources</h4>
<p className="craik-adr-card__decision">
Registries declaring which project files Craik may use for runtime
instruction distillation. Craik does not treat every Markdown file as
an instruction by default.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

</ol>

<header className="craik-section-banner">
<div className="craik-section-banner__num" aria-hidden="true">04</div>
<div className="craik-section-banner__body">
<p className="craik-section-banner__kicker">Agents, context &amp; learning</p>
<h3 className="craik-section-banner__title">
How agents onboard, budget context, and <em>feed back into the runtime.</em>
</h3>
<p className="craik-section-banner__lede">
Fifteen docs cover the agent lifecycle: onboarding, context budgeting
and debt, scratchpad rules, exit discipline, knowledge boundaries
(traps, freshness, quality), the learning loop, and the multi-agent
coordination primitives. Every typed object here is reviewable —
nothing rewrites itself silently.
</p>
</div>
</header>

<div className="craik-product-spread">

<a className="craik-product-feature" href="guides/agent-onboarding.md">
<div>
<p className="craik-product-feature__num">Onboarding · 01</p>
<h4 className="craik-product-feature__title">Agent onboarding</h4>
<p className="craik-product-feature__summary">
<code>craik onboard</code> emits the canonical
<code>craik.agent_onboarding</code> payload — project model, policy
envelope, docs boundaries, recent handoffs, unresolved contradictions,
stale-risk warnings, validation commands, Stigmem backend status,
known traps, and allowed next actions.
</p>
<ul className="craik-product-feature__topics">
<li>onboarding payload</li>
<li>policy envelope</li>
<li>continuity context</li>
<li>safe for runners</li>
</ul>
<span className="craik-product-feature__cta">Run onboarding</span>
</div>
<blockquote className="craik-product-feature__quote">
<p className="craik-product-feature__quote-eyebrow">Before any work</p>
<p className="craik-product-feature__quote-text">
Use onboarding before starting project work. The command prints a
JSON <code>craik.agent_onboarding</code> report — safe for runners to
parse directly.
</p>
<p className="craik-product-feature__quote-attribution">— Agent onboarding · §Intro</p>
</blockquote>
</a>

</div>

<ol className="craik-adr-grid">

<li>
<a className="craik-adr-card" href="guides/context-budgeting.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">02</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Guide · context</span>
</div>
<h4 className="craik-adr-card__title">Context budgeting</h4>
<p className="craik-adr-card__decision">
Case files are bounded. The context budget records what was included
and what was omitted — every cut is auditable, every inclusion is
justifiable.
</p>
<span className="craik-adr-card__cta">Guide</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/context-debt.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">03</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · context</span>
</div>
<h4 className="craik-adr-card__title">Context debt</h4>
<p className="craik-adr-card__decision">
Records preserve known gaps in the context an agent used. Future
agents decide whether to continue, refresh, or stop — instead of
inheriting silent omissions.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/scratchpad-and-unknowns.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">04</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · context</span>
</div>
<h4 className="craik-adr-card__title">Scratchpad &amp; unknowns</h4>
<p className="craik-adr-card__decision">
Scratchpad records are temporary working notes. They must expire and
must not be treated as durable context unless promoted through an
explicit review path.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/exit-discipline.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">05</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · context</span>
</div>
<h4 className="craik-adr-card__title">Context requests &amp; exit discipline</h4>
<p className="craik-adr-card__decision">
Structured asks for information needed before work can continue
safely. Link to handoffs, recovery sessions, and unresolved
delegation points so a stop is never silent.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/known-traps.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">06</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · knowledge</span>
</div>
<h4 className="craik-adr-card__title">Known traps &amp; negative knowledge</h4>
<p className="craik-adr-card__decision">
Evidence-backed pitfalls agents should avoid, plus statements about
what is <em>not</em> true or <em>not</em> available. Negative
knowledge is first-class, not implied by absence.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/freshness.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">07</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · knowledge</span>
</div>
<h4 className="craik-adr-card__title">Tool attestations &amp; freshness</h4>
<p className="craik-adr-card__decision">
Attestations record observed command or tool results with a trust
boundary. Freshness probes track when knowledge should be considered
fresh, expiring, or stale.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/quality-scores.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">08</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · knowledge</span>
</div>
<h4 className="craik-adr-card__title">Quality scores</h4>
<p className="craik-adr-card__decision">
Derived review records. They help agents decide whether a handoff or
evidence set is ready to rely on — but they are not proof of truth
or a substitute for evidence.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="guides/learning-loops.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">09</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Guide · learning</span>
</div>
<h4 className="craik-adr-card__title">Learning loops</h4>
<p className="craik-adr-card__decision">
Turn observed skill behavior into reviewable improvement records.
Loops do not let an agent silently rewrite reusable guidance —
proposals route through the skill promotion gates.
</p>
<span className="craik-adr-card__cta">Guide</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/learning-receipts.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">10</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · learning</span>
</div>
<h4 className="craik-adr-card__title">Learning receipts</h4>
<p className="craik-adr-card__decision">
Normal <code>craik.capability_receipt</code> records for
self-improvement decisions. Every promotion or rollback is receipted
the same way every other governed action is.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/trajectory-exports.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">11</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · learning</span>
</div>
<h4 className="craik-adr-card__title">Training trajectory exports</h4>
<p className="craik-adr-card__decision">
Stable review and replay format for self-improvement loops. Exports
are deterministic, redacted, and joinable to the runs that produced
the trajectory.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/cross-agent-review.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">12</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · multi-agent</span>
</div>
<h4 className="craik-adr-card__title">Cross-agent review</h4>
<p className="craik-adr-card__decision">
Lets one specialist role request review from another without
collapsing distinct decisions into a single worker result.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/debates.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">13</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · multi-agent</span>
</div>
<h4 className="craik-adr-card__title">Structured debates</h4>
<p className="craik-adr-card__decision">
Captures bounded multi-agent disagreement without erasing minority
positions. Debates are coordination records, not a consensus
mechanism.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/human-delegation.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">14</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · multi-agent</span>
</div>
<h4 className="craik-adr-card__title">Human delegation &amp; scope changes</h4>
<p className="craik-adr-card__decision">
Human delegation points mark places where autonomous agents must stop
or hand off instead of continuing silently. The "ask a human" surface
is itself a typed object.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="reference/runtime-critics.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">15</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Contract · multi-agent</span>
</div>
<h4 className="craik-adr-card__title">Runtime critics &amp; red team</h4>
<p className="craik-adr-card__decision">
Critic and red-team findings are typed review inputs — not facts,
final decisions, or policy overrides — until a separate adjudication
accepts them.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

</ol>

### 5 · Gateway & channels

Running Craik as a daemon, ingesting messages from channels, and binding
identity at the boundary.

- [Gateway daemon mode](reference/gateway-daemon.md)
- [Gateway troubleshooting](guides/gateway-troubleshooting.md)
- [Channel adapter contract](reference/channel-adapter-contract.md)
- [Messaging channel adapter](reference/messaging-channel-adapter.md)
- [Channel identity pairing](reference/channel-identity-pairing.md)
- [Channel allowlists](reference/channel-allowlists.md)
- [Channel policy envelopes](reference/channel-policy-envelopes.md)
- [Webhook ingress](reference/webhook-ingress.md)
- [Scheduled task creation](reference/scheduled-task-creation.md)
- [Scheduled automations](reference/scheduled-automations.md)
- [Gateway receipts](reference/gateway-receipts.md)

### 6 · Companion apps & visual workspaces

Decisions and contracts for the desktop, mobile, and live visual workspace
surfaces.

- [Companion app security](guides/companion-app-security.md)
- [Desktop companion decision](reference/desktop-companion.md)
- [Mobile companion decision](reference/mobile-companion.md)
- [Live visual workspace decision](reference/visual-workspace.md)
- [Work graph visual workspace bridge](reference/work-graph-visual-bridge.md)
- [Accessibility requirements](reference/accessibility-requirements.md)

### 7 · Multimodal & voice

Contracts for handling images, audio, and other non-text artifacts.

- [Multimodal artifact references](reference/multimodal-artifacts.md)
- [Voice input & output posture](reference/voice-posture.md)
- [Speech-to-text adapter contract](reference/speech-to-text-adapters.md)
- [Text-to-speech adapter contract](reference/text-to-speech-adapters.md)

### 8 · Translation & locale

How non-English contributors and operators can use Craik.

- [Translated documentation strategy](guides/translated-docs.md)
- [Locale i18n framework](reference/locale-i18n-framework.md)

## Where to go next

- **Build something new** → [Build](build.md)
- **Govern execution** → [Secure](secure.md)
- **Understand the model** → [Learn](learn.md)
