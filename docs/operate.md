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

### 3 · Operator views

What an operator sees during and after a governed run. The work graph,
handoffs, receipts, contradictions, and the various inspection surfaces are all
addressable as named views.

- [Operator surface](reference/operator-surface.md)
- [Work graph explorer](reference/work-graph-explorer.md)
- [Handoff viewer](reference/handoff-viewer.md)
- [Receipt viewer](reference/receipt-viewer.md)
- [Contradiction inbox view](reference/contradiction-inbox-view.md)
- [Evidence & assumption view](reference/evidence-assumption-view.md)
- [Delegation queue view](reference/delegation-queue-view.md)
- [Budget & quota view](reference/budget-quota-view.md)
- [Quality gate view](reference/quality-gate-view.md)
- [Run delta view](reference/run-delta-view.md)
- [Memory impact preview view](reference/memory-impact-preview-view.md)
- [Memory review nudges](reference/memory-review-nudges.md)
- [Known traps view](reference/known-traps-view.md)
- [Preference facts](reference/preference-facts.md)
- [Instruction distillation view](reference/instruction-distillation-view.md)
- [Instruction distillation workflow](reference/instruction-distillation-workflow.md)
- [Instruction sources](reference/instruction-sources.md)

### 4 · Agents, context & learning loops

How agents onboard, how context is budgeted, and how quality signals feed back
into the runtime over time.

- [Agent onboarding](guides/agent-onboarding.md)
- [Context budgeting](guides/context-budgeting.md)
- [Context debt](reference/context-debt.md)
- [Scratchpad & unknowns](reference/scratchpad-and-unknowns.md)
- [Exit discipline](reference/exit-discipline.md)
- [Known traps & negative knowledge](reference/known-traps.md)
- [Tool attestations & freshness](reference/freshness.md)
- [Quality scores](reference/quality-scores.md)
- [Learning loops](guides/learning-loops.md)
- [Learning receipts](reference/learning-receipts.md)
- [Trajectory exports](reference/trajectory-exports.md)
- [Cross-agent review](reference/cross-agent-review.md)
- [Structured debates](reference/debates.md)
- [Human delegation](reference/human-delegation.md)
- [Runtime critics & red team](reference/runtime-critics.md)

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
