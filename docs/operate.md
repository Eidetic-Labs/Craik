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

### 1 · Day-to-day operations

The commands you reach for most often. Start here if you're picking up an
already-running install.

- [Development checks](guides/development.md)
- [Doctor diagnostics](guides/doctor.md)
- [Updating Craik](guides/updating.md)
- [Release management](guides/release-management.md)

### 2 · Local state & migrations

Where Craik stores things on disk, how to upgrade those stores, and how secret
material moves.

- [Local state](reference/local-state.md)
- [Local store](reference/local-store.md)
- [Local store migrations](guides/local-store-migrations.md)
- [Secret migration policy](reference/secret-migration-policy.md)

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
