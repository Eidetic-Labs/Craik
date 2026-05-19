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

- [Development checks](/docs/guides/development)
- [Doctor diagnostics](/docs/guides/doctor)
- [Updating Craik](/docs/guides/updating)
- [Release management](/docs/guides/release-management)

### 2 · Local state & migrations

Where Craik stores things on disk, how to upgrade those stores, and how secret
material moves.

- [Local state](/docs/reference/local-state)
- [Local store](/docs/reference/local-store)
- [Local store migrations](/docs/guides/local-store-migrations)
- [Secret migration policy](/docs/reference/secret-migration-policy)

### 3 · Operator views

What an operator sees during and after a governed run. The work graph,
handoffs, receipts, contradictions, and the various inspection surfaces are all
addressable as named views.

- [Operator surface](/docs/reference/operator-surface)
- [Work graph explorer](/docs/reference/work-graph-explorer)
- [Handoff viewer](/docs/reference/handoff-viewer)
- [Receipt viewer](/docs/reference/receipt-viewer)
- [Contradiction inbox view](/docs/reference/contradiction-inbox-view)
- [Evidence & assumption view](/docs/reference/evidence-assumption-view)
- [Delegation queue view](/docs/reference/delegation-queue-view)
- [Budget & quota view](/docs/reference/budget-quota-view)
- [Quality gate view](/docs/reference/quality-gate-view)
- [Run delta view](/docs/reference/run-delta-view)
- [Memory impact preview view](/docs/reference/memory-impact-preview-view)
- [Memory review nudges](/docs/reference/memory-review-nudges)
- [Known traps view](/docs/reference/known-traps-view)
- [Preference facts](/docs/reference/preference-facts)
- [Instruction distillation view](/docs/reference/instruction-distillation-view)
- [Instruction distillation workflow](/docs/reference/instruction-distillation-workflow)
- [Instruction sources](/docs/reference/instruction-sources)

### 4 · Agents, context & learning loops

How agents onboard, how context is budgeted, and how quality signals feed back
into the runtime over time.

- [Agent onboarding](/docs/guides/agent-onboarding)
- [Context budgeting](/docs/guides/context-budgeting)
- [Context debt](/docs/reference/context-debt)
- [Scratchpad & unknowns](/docs/reference/scratchpad-and-unknowns)
- [Exit discipline](/docs/reference/exit-discipline)
- [Known traps & negative knowledge](/docs/reference/known-traps)
- [Tool attestations & freshness](/docs/reference/freshness)
- [Quality scores](/docs/reference/quality-scores)
- [Learning loops](/docs/guides/learning-loops)
- [Learning receipts](/docs/reference/learning-receipts)
- [Trajectory exports](/docs/reference/trajectory-exports)
- [Cross-agent review](/docs/reference/cross-agent-review)
- [Structured debates](/docs/reference/debates)
- [Human delegation](/docs/reference/human-delegation)
- [Runtime critics & red team](/docs/reference/runtime-critics)

### 5 · Gateway & channels

Running Craik as a daemon, ingesting messages from channels, and binding
identity at the boundary.

- [Gateway daemon mode](/docs/reference/gateway-daemon)
- [Gateway troubleshooting](/docs/guides/gateway-troubleshooting)
- [Channel adapter contract](/docs/reference/channel-adapter-contract)
- [Messaging channel adapter](/docs/reference/messaging-channel-adapter)
- [Channel identity pairing](/docs/reference/channel-identity-pairing)
- [Channel allowlists](/docs/reference/channel-allowlists)
- [Channel policy envelopes](/docs/reference/channel-policy-envelopes)
- [Webhook ingress](/docs/reference/webhook-ingress)
- [Scheduled task creation](/docs/reference/scheduled-task-creation)
- [Scheduled automations](/docs/reference/scheduled-automations)
- [Gateway receipts](/docs/reference/gateway-receipts)

### 6 · Companion apps & visual workspaces

Decisions and contracts for the desktop, mobile, and live visual workspace
surfaces.

- [Companion app security](/docs/guides/companion-app-security)
- [Desktop companion decision](/docs/reference/desktop-companion)
- [Mobile companion decision](/docs/reference/mobile-companion)
- [Live visual workspace decision](/docs/reference/visual-workspace)
- [Work graph visual workspace bridge](/docs/reference/work-graph-visual-bridge)
- [Accessibility requirements](/docs/reference/accessibility-requirements)

### 7 · Multimodal & voice

Contracts for handling images, audio, and other non-text artifacts.

- [Multimodal artifact references](/docs/reference/multimodal-artifacts)
- [Voice input & output posture](/docs/reference/voice-posture)
- [Speech-to-text adapter contract](/docs/reference/speech-to-text-adapters)
- [Text-to-speech adapter contract](/docs/reference/text-to-speech-adapters)

### 8 · Translation & locale

How non-English contributors and operators can use Craik.

- [Translated documentation strategy](/docs/guides/translated-docs)
- [Locale i18n framework](/docs/reference/locale-i18n-framework)

## Where to go next

- **Build something new** → [Build](/docs/build)
- **Govern execution** → [Secure](/docs/secure)
- **Understand the model** → [Learn](/docs/learn)
