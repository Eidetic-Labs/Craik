---
id: learn
title: Learn
sidebar_label: Overview
sidebar_position: 0
description: Understand what Craik is, the runtime mental model, and where the project is going.
slug: /learn
---

# Learn Craik

Craik is a **governed agent-runtime substrate** — the operating layer that turns
coding agents from isolated chat sessions into accountable project workers. This
section explains what that means, the typed objects the runtime is built from,
and how the project intends to grow.

If you'd rather jump straight to installing the CLI, head to
[Build → Getting started](guides/installation.md).

## What's in this section

<header className="craik-section-banner">
<div className="craik-section-banner__num" aria-hidden="true">01</div>
<div className="craik-section-banner__body">
<p className="craik-section-banner__kicker">The product</p>
<h3 className="craik-section-banner__title">
A durable agent runtime — <em>not another framework.</em>
</h3>
<p className="craik-section-banner__lede">
Start here to understand the thesis: agent work needs an
<strong> operating layer</strong> — not more clever prompting — and the
five docs below build that argument from the north star down through
the typed contracts. Every other section of these docs is downstream
of this one.
</p>
</div>
</header>

<div className="craik-product-spread">

<a className="craik-product-feature" href="../vision/">
<div>
<p className="craik-product-feature__num">Featured · 01</p>
<h4 className="craik-product-feature__title">Vision</h4>
<p className="craik-product-feature__summary">
Craik's central claim is that agents need an operating layer that gives
them a shared model of the work, evidence-backed memory, explicit authority
boundaries, structured handoffs, durable artifacts, and a way to resolve
disagreement. Read this first — every other doc is downstream of it.
</p>
<ul className="craik-product-feature__topics">
<li>durable agent runtime</li>
<li>north star</li>
<li>design principles</li>
<li>initial wedge</li>
</ul>
<span className="craik-product-feature__cta">Read the vision</span>
</div>
<blockquote className="craik-product-feature__quote">
<p className="craik-product-feature__quote-eyebrow">North star</p>
<p className="craik-product-feature__quote-text">
A new agent should be able to join a project and understand its current
state better than a human who has been away for two weeks.
</p>
<p className="craik-product-feature__quote-attribution">— Vision · §North Star</p>
</blockquote>
</a>

<ol className="craik-product-list">

<li>
<a className="craik-product-card" href="../product-strategy/">
<svg className="craik-card-motif" viewBox="0 0 64 64" aria-hidden="true">
<circle cx="12" cy="18" r="3" />
<circle cx="52" cy="18" r="3" />
<circle cx="32" cy="54" r="3" />
<line x1="12" y1="18" x2="30" y2="32" />
<line x1="52" y1="18" x2="34" y2="32" />
<line x1="32" y1="54" x2="32" y2="34" />
<circle cx="32" cy="32" r="5" fill="var(--craik-lavender)" stroke="none" />
</svg>
<p className="craik-product-card__num">02 · Positioning</p>
<h4 className="craik-product-card__title">Product strategy</h4>
<p className="craik-product-card__summary">
Why Craik is a <em>durable agent runtime</em>, not a framework. The
market wedge, the agent-runner strategy (Codex / Claude / Gemini as
first-class adapters), the MIT license rationale, and the patterns Craik
borrows from local runtimes versus the patterns it adds on top.
</p>
<blockquote className="craik-product-card__quote">
Craik should not be positioned as another agent framework.
<span className="craik-product-card__quote-attr">Product strategy · §Agent Runner Strategy</span>
</blockquote>
<ul className="craik-product-card__topics">
<li>runner strategy</li>
<li>license</li>
<li>gateway ergonomics</li>
<li>multi-agent coordination</li>
</ul>
<p className="craik-product-card__meta">
<span>For: founders &middot; product</span>
<span className="craik-product-card__cta">5 min read</span>
</p>
</a>
</li>

<li>
<a className="craik-product-card" href="../differentiators/">
<svg className="craik-card-motif" viewBox="0 0 64 64" aria-hidden="true">
<line x1="8" y1="32" x2="30" y2="32" />
<line x1="34" y1="32" x2="56" y2="14" />
<line x1="34" y1="32" x2="56" y2="50" stroke-dasharray="3.5 3" />
<circle cx="32" cy="32" r="3" fill="var(--craik-lavender)" stroke="none" />
<circle cx="56" cy="14" r="2.5" />
<circle cx="56" cy="50" r="2.5" stroke-dasharray="2 2" />
</svg>
<p className="craik-product-card__num">03 · What's distinct</p>
<h4 className="craik-product-card__title">Differentiators</h4>
<p className="craik-product-card__summary">
The features that keep the roadmap from collapsing into basic CLI
plumbing. Evidence-first execution, the assumption ledger, the
belief-promotion lifecycle, context budgeting as policy, and end-to-end
run reproducibility.
</p>
<blockquote className="craik-product-card__quote">
No durable assertion without evidence.
<span className="craik-product-card__quote-attr">Differentiators · §Evidence-First Execution</span>
</blockquote>
<ul className="craik-product-card__topics">
<li>evidence-first</li>
<li>assumption ledger</li>
<li>belief promotion</li>
<li>reproducibility</li>
</ul>
<p className="craik-product-card__meta">
<span>For: engineers &middot; reviewers</span>
<span className="craik-product-card__cta">10 min read</span>
</p>
</a>
</li>

<li>
<a className="craik-product-card" href="../features/">
<svg className="craik-card-motif" viewBox="0 0 64 64" aria-hidden="true">
<line x1="18" y1="14" x2="54" y2="14" />
<line x1="18" y1="22" x2="48" y2="22" />
<line x1="18" y1="30" x2="54" y2="30" />
<line x1="18" y1="38" x2="42" y2="38" />
<line x1="18" y1="46" x2="54" y2="46" />
<line x1="18" y1="54" x2="46" y2="54" />
<circle cx="10" cy="30" r="2.5" fill="var(--craik-lavender)" stroke="none" />
</svg>
<p className="craik-product-card__num">04 · What ships</p>
<h4 className="craik-product-card__title">Features</h4>
<p className="craik-product-card__summary">
The implementable feature surface — every MVP behavior with acceptance
criteria. Project registry, case-file assembler, policy envelope,
capability grants, runner adapters, work graph, receipts, handoffs.
Read this to know exactly what v0.1 ships.
</p>
<blockquote className="craik-product-card__quote">
Read-only tasks default to repo read, memory read, and receipt write.
Implementation tasks require explicit write grants.
<span className="craik-product-card__quote-attr">Features · §Policy Envelope</span>
</blockquote>
<ul className="craik-product-card__topics">
<li>case files</li>
<li>policy envelope</li>
<li>receipts</li>
<li>handoffs</li>
<li>work graph</li>
</ul>
<p className="craik-product-card__meta">
<span>For: implementers</span>
<span className="craik-product-card__cta">10 min read</span>
</p>
</a>
</li>

<li>
<a className="craik-product-card" href="../architecture/">
<svg className="craik-card-motif" viewBox="0 0 64 64" aria-hidden="true">
<rect x="10" y="8" width="44" height="3.5" rx="1" />
<rect x="14" y="16" width="36" height="3.5" rx="1" />
<rect x="10" y="24" width="44" height="3.5" rx="1" />
<rect x="14" y="32" width="36" height="3.5" rx="1" />
<rect x="10" y="40" width="44" height="3.5" rx="1" />
<rect x="14" y="48" width="36" height="3.5" rx="1" />
<rect x="22" y="56" width="20" height="3.5" rx="1" fill="var(--craik-lavender)" stroke="none" />
</svg>
<p className="craik-product-card__num">05 · How it composes</p>
<h4 className="craik-product-card__title">Architecture</h4>
<p className="craik-product-card__summary">
The seven runtime layers — gateway, project model, orchestration, runner
adapters, capability, memory, work graph, experience — plus the typed
contracts that hold them together. The map for anyone extending Craik
or integrating a new runner.
</p>
<blockquote className="craik-product-card__quote">
The layers should remain separable so Craik can support different model
providers, tool environments, and memory backends without weakening the
product thesis.
<span className="craik-product-card__quote-attr">Architecture · §Layers</span>
</blockquote>
<ul className="craik-product-card__topics">
<li>seven layers</li>
<li>runtime flow</li>
<li>core contracts</li>
<li>borrowed patterns</li>
</ul>
<p className="craik-product-card__meta">
<span>For: architects &middot; contributors</span>
<span className="craik-product-card__cta">4 min read</span>
</p>
</a>
</li>

</ol>

</div>

### 2 · Core concepts

Read these in order on your first pass. Each concept maps to a typed runtime
object that the rest of the docs reference by name.

1. [Project model](concepts/project-model.md)
2. [Case files](concepts/case-files.md)
3. [Single-agent execution loop](concepts/single-agent-loop.md)
4. [Receipts](concepts/receipts.md)
5. [Handoffs](concepts/handoffs.md)
6. [Work graph](concepts/work-graph.md)
7. [Memory & Stigmem](concepts/memory-and-stigmem.md)
8. [Governance](concepts/governance.md)
9. [Intent locks](concepts/intent-locks.md)

### 3 · Runtime contracts

The typed objects every Craik component speaks. Read these when you need to
implement an adapter, write a policy, or interpret a receipt.

- [Runtime contracts overview](runtime-contracts.md)
- [Schemas](reference/schemas.md)
- [Project profile](reference/project-profile.md)
- [Run state](reference/run-state.md)
- [Worker results](reference/worker-results.md)
- [Failure modes](reference/failure-modes.md)

### 4 · Status & roadmap

Where Craik is today and where it is going. Honest about what's not yet built.

- [Current MVP](mvp.md)
- [MVP roadmap](mvp-roadmap.md)
- [Roadmap](roadmap.md)
- [Release readiness · v0.1.0](release-readiness.md)
- [Limitations](limitations.md)
- [Implementation plan](implementation-plan.md)

### 5 · Architecture Decision Records

The reasons behind the structural choices. Stable, dated, and referenced from
the rest of the docs.

- [ADR index](adr/index.md)
- ADR 0001 — [MVP runner scope](adr/0001-record-mvp-runner-scope.md)
- ADR 0002 — [Provider transport and mode families](adr/0002-provider-transport-and-mode-families.md)
- ADR 0003 — [Secret handling](adr/0003-secret-handling.md)
- ADR 0004 — [Policy envelope shape](adr/0004-policy-envelope-shape.md)
- ADR 0005 — [Receipts and handoffs as public contracts](adr/0005-receipts-and-handoffs-as-public-contracts.md)
- ADR 0006 — [Package and runtime layout](adr/0006-package-and-runtime-layout.md)
- ADR 0007 — [Credential and identity architecture](adr/0007-credential-and-identity-architecture.md)

### 6 · Stigmem integration

Craik runs in degraded local mode without Stigmem, but Stigmem is the reference
substrate for team-scale memory.

- [Stigmem integration](stigmem-integration.md)

## Where to go next

Once the concepts are clear, choose your path:

- **Install and run something** → [Build · Getting started](guides/installation.md)
- **Integrate a runner or provider** → [Build · Connecting runners](reference/runner-adapter-contract.md)
- **Govern execution** → [Secure · Governance fundamentals](concepts/governance.md)
- **Run and inspect the system** → [Operate · Operator views](reference/operator-surface.md)
