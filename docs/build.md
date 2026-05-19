---
id: build
title: Build
sidebar_label: Overview
sidebar_position: 0
description: Install Craik, register projects, connect runners and providers, and put the runtime to work.
slug: /build
---

# Build with Craik

This section is task-oriented. Every page either gets you to a running Craik
surface or documents a contract you implement against. Topics are grouped by
**what you are trying to build**, and each group lists the guides and reference
in the order most teams reach for them.

If you've never seen Craik before, do these three things first:

1. [Install Craik](guides/installation.md)
2. [Quickstart](guides/quickstart.md)
3. [Register a project](guides/project-registry.md)

## Implementation paths

<header className="craik-section-banner">
<div className="craik-section-banner__num" aria-hidden="true">01</div>
<div className="craik-section-banner__body">
<p className="craik-section-banner__kicker">Getting started</p>
<h3 className="craik-section-banner__title">
From zero to a <em>governed first run.</em>
</h3>
<p className="craik-section-banner__lede">
Install the CLI, point it at a repository, initialize the home
directory, and walk a complete governed task — without making a single
live provider call. Four docs, in order.
</p>
</div>
</header>

<div className="craik-product-spread">

<a className="craik-product-feature" href="guides/quickstart.md">
<div>
<p className="craik-product-feature__num">Hands-on · 01</p>
<h4 className="craik-product-feature__title">Quickstart</h4>
<p className="craik-product-feature__summary">
A 10-minute narrative tutorial: sandbox the Craik home, register a
project, create a task, build a case file, run the policy gate, emit a
handoff, and inspect what landed on disk. Uses the fixture-backed
provider path — zero credentials, zero network.
</p>
<ul className="craik-product-feature__topics">
<li>sandboxed home</li>
<li>case file + policy gate</li>
<li>handoff</li>
<li>stigmem demo</li>
</ul>
<span className="craik-product-feature__cta">Walk the quickstart</span>
</div>
<blockquote className="craik-product-feature__quote">
<p className="craik-product-feature__quote-eyebrow">What you'll do</p>
<p className="craik-product-feature__quote-text">
Install Craik, point it at a Git repository, build a case file, run
policy tests, and emit a handoff — without making a single live
provider call. Every output we discuss is real and persists on disk.
</p>
<p className="craik-product-feature__quote-attribution">— Quickstart · §What you'll do</p>
</blockquote>
</a>

<ol className="craik-product-list">

<li>
<a className="craik-product-card" href="guides/installation.md">
<svg className="craik-card-motif" viewBox="0 0 64 64" aria-hidden="true">
<rect x="14" y="20" width="36" height="28" rx="3" />
<path d="M 32 14 L 32 30" />
<path d="M 26 24 L 32 30 L 38 24" />
<circle cx="20" cy="42" r="2" fill="var(--craik-lavender)" stroke="none" />
</svg>
<p className="craik-product-card__num">02 · Front door</p>
<h4 className="craik-product-card__title">Installation</h4>
<p className="craik-product-card__summary">
Prerequisites, three install paths (<code>pipx</code> / <code>pip</code>
/ source), verification commands, home initialization, optional auth,
and a troubleshooting matrix for the most common first-run issues.
</p>
<blockquote className="craik-product-card__quote">
Craik is a Python CLI. You need a recent Python interpreter and a way
to put the CLI on your PATH.
<span className="craik-product-card__quote-attr">Installation · §Prerequisites</span>
</blockquote>
<ul className="craik-product-card__topics">
<li>python 3.12+</li>
<li>pipx / pip</li>
<li>verification</li>
<li>troubleshooting</li>
</ul>
<p className="craik-product-card__meta">
<span>For: everyone</span>
<span className="craik-product-card__cta">3 min read</span>
</p>
</a>
</li>

<li>
<a className="craik-product-card" href="guides/setup.md">
<svg className="craik-card-motif" viewBox="0 0 64 64" aria-hidden="true">
<circle cx="32" cy="32" r="14" />
<circle cx="32" cy="32" r="6" fill="var(--craik-lavender)" stroke="none" />
<line x1="32" y1="10" x2="32" y2="18" />
<line x1="54" y1="32" x2="46" y2="32" />
<line x1="32" y1="54" x2="32" y2="46" />
<line x1="10" y1="32" x2="18" y2="32" />
</svg>
<p className="craik-product-card__num">03 · Wire it up</p>
<h4 className="craik-product-card__title">Setup wizard</h4>
<p className="craik-product-card__summary">
<code>craik setup</code> initializes the local home, the SQLite store,
and a default gateway configuration. Writes inspectable, non-secret
configuration only. Authentication and credentials are added separately
after setup completes.
</p>
<blockquote className="craik-product-card__quote">
The wizard writes inspectable, non-secret configuration only. It does
not ask for API keys, channel tokens, webhook secrets, or bearer
credentials.
<span className="craik-product-card__quote-attr">Setup · §Secrets-free</span>
</blockquote>
<ul className="craik-product-card__topics">
<li>home init</li>
<li>local store</li>
<li>gateway config</li>
<li>secrets-free</li>
</ul>
<p className="craik-product-card__meta">
<span>For: first-time operators</span>
<span className="craik-product-card__cta">4 min read</span>
</p>
</a>
</li>

<li>
<a className="craik-product-card" href="guides/configuring-craik-home.md">
<svg className="craik-card-motif" viewBox="0 0 64 64" aria-hidden="true">
<path d="M 14 30 L 32 14 L 50 30 L 50 50 L 14 50 Z" />
<rect x="22" y="34" width="20" height="16" />
<circle cx="46" cy="20" r="2.5" fill="var(--craik-lavender)" stroke="none" />
</svg>
<p className="craik-product-card__num">04 · Where state lives</p>
<h4 className="craik-product-card__title">Configuring Craik home</h4>
<p className="craik-product-card__summary">
The default <code>~/.craik/</code> layout, overrides via
<code>CRAIK_HOME</code>, share patterns for CI runners and containerized
runs, and the reset procedure. Read this before pointing Craik at a
network share.
</p>
<blockquote className="craik-product-card__quote">
Craik does NOT silently create project-local <code>.craik/</code>
directories inside your repositories.
<span className="craik-product-card__quote-attr">Configuring home · §Default location</span>
</blockquote>
<ul className="craik-product-card__topics">
<li>home layout</li>
<li>CRAIK_HOME</li>
<li>CI runners</li>
<li>reset</li>
</ul>
<p className="craik-product-card__meta">
<span>For: operators</span>
<span className="craik-product-card__cta">4 min read</span>
</p>
</a>
</li>

</ol>

</div>

<header className="craik-section-banner">
<div className="craik-section-banner__num" aria-hidden="true">02</div>
<div className="craik-section-banner__body">
<p className="craik-section-banner__kicker">Working with projects</p>
<h3 className="craik-section-banner__title">
Repositories become <em>typed, queryable projects.</em>
</h3>
<p className="craik-section-banner__lede">
The project profile is the durable representation of a repository.
Case files are the per-task brief built from it. Handoffs are how runs
end. These four docs cover the full project-to-handoff lifecycle.
</p>
</div>
</header>

<div className="craik-product-spread">

<a className="craik-product-feature" href="guides/project-registry.md">
<div>
<p className="craik-product-feature__num">Entry point · 01</p>
<h4 className="craik-product-feature__title">Project registry</h4>
<p className="craik-product-feature__summary">
Register a Git repository as a Craik project. Declares mutable docs
paths, immutable evidence paths, and (optionally) a memory backend.
Project records persist in the local SQLite store — Craik never writes
into your repository.
</p>
<ul className="craik-product-feature__topics">
<li>boundaries</li>
<li>multi-project</li>
<li>inspect via onboard</li>
<li>local-only state</li>
</ul>
<span className="craik-product-feature__cta">Register a project</span>
</div>
<blockquote className="craik-product-feature__quote">
<p className="craik-product-feature__quote-eyebrow">Where state lives</p>
<p className="craik-product-feature__quote-text">
Registration writes only to Craik local state under <code>~/.craik</code>
or <code>$CRAIK_HOME</code>. It does not create project-local
<code>.craik/</code> metadata inside the repository.
</p>
<p className="craik-product-feature__quote-attribution">— Project registry · §Where state lives</p>
</blockquote>
</a>

<ol className="craik-product-list">

<li>
<a className="craik-product-card" href="reference/project-profile.md">
<svg className="craik-card-motif" viewBox="0 0 64 64" aria-hidden="true">
<rect x="14" y="14" width="36" height="36" rx="2" />
<line x1="14" y1="22" x2="50" y2="22" />
<line x1="20" y1="30" x2="44" y2="30" />
<line x1="20" y1="36" x2="40" y2="36" />
<line x1="20" y1="42" x2="44" y2="42" />
<circle cx="18" cy="18" r="1.5" fill="var(--craik-lavender)" stroke="none" />
</svg>
<p className="craik-product-card__num">02 · Typed object</p>
<h4 className="craik-product-card__title">Project profile reference</h4>
<p className="craik-product-card__summary">
The <code>craik.project_profile</code> shape: stable id, repo paths,
default branch, docs and immutable paths, memory backend and scope.
Every case-file build and onboarding payload reads against this.
</p>
<blockquote className="craik-product-card__quote">
Project profiles describe repositories Craik can reason about.
<span className="craik-product-card__quote-attr">Project profile · §Intro</span>
</blockquote>
<ul className="craik-product-card__topics">
<li>repo metadata</li>
<li>docs boundaries</li>
<li>memory backend</li>
<li>git detection</li>
</ul>
<p className="craik-product-card__meta">
<span>For: integrators</span>
<span className="craik-product-card__cta">Reference</span>
</p>
</a>
</li>

<li>
<a className="craik-product-card" href="guides/using-case-files.md">
<svg className="craik-card-motif" viewBox="0 0 64 64" aria-hidden="true">
<path d="M 14 14 L 14 50 L 50 50 L 50 22 L 42 14 Z" />
<path d="M 42 14 L 42 22 L 50 22" />
<line x1="22" y1="32" x2="42" y2="32" />
<line x1="22" y1="38" x2="38" y2="38" />
<line x1="22" y1="44" x2="42" y2="44" />
<circle cx="46" cy="46" r="2" fill="var(--craik-lavender)" stroke="none" />
</svg>
<p className="craik-product-card__num">03 · Pre-run brief</p>
<h4 className="craik-product-card__title">Using case files</h4>
<p className="craik-product-card__summary">
Build, inspect, and refresh per-task case files. Discovery overrides,
the 10 fields to review before authorizing a run, and how to handle
open assumptions as first-class — not bugs.
</p>
<blockquote className="craik-product-card__quote">
Case files are only as good as the project they're built against.
<span className="craik-product-card__quote-attr">Using case files · §Tune discovery</span>
</blockquote>
<ul className="craik-product-card__topics">
<li>case build</li>
<li>discovery overrides</li>
<li>assumptions</li>
<li>refresh procedure</li>
</ul>
<p className="craik-product-card__meta">
<span>For: operators</span>
<span className="craik-product-card__cta">6 min read</span>
</p>
</a>
</li>

<li>
<a className="craik-product-card" href="guides/writing-handoffs.md">
<svg className="craik-card-motif" viewBox="0 0 64 64" aria-hidden="true">
<circle cx="16" cy="32" r="5" />
<circle cx="48" cy="32" r="5" fill="var(--craik-lavender)" stroke="none" />
<line x1="22" y1="32" x2="40" y2="32" />
<path d="M 36 26 L 42 32 L 36 38" />
<rect x="10" y="48" width="44" height="6" rx="1" />
</svg>
<p className="craik-product-card__num">04 · Continuity</p>
<h4 className="craik-product-card__title">Writing handoffs</h4>
<p className="craik-product-card__summary">
Status semantics (<code>completed/incomplete/blocked/failed</code>),
the eight things every handoff should include, anti-patterns that hurt
the next agent, and the six self-audit checks that keep incomplete
runs honest.
</p>
<blockquote className="craik-product-card__quote">
Incomplete handoffs are valid. Dishonest handoffs are not — they
contaminate the next run's context.
<span className="craik-product-card__quote-attr">Writing handoffs · §Self-audit</span>
</blockquote>
<ul className="craik-product-card__topics">
<li>status semantics</li>
<li>anti-patterns</li>
<li>self-audit</li>
<li>continuity</li>
</ul>
<p className="craik-product-card__meta">
<span>For: runners &middot; humans</span>
<span className="craik-product-card__cta">5 min read</span>
</p>
</a>
</li>

</ol>

</div>

### 3 · Connecting a runner

Codex, Claude, Gemini — or your own. Every runner consumes the same contracts.

- [Runner adapter contract](reference/runner-adapter-contract.md)
- [Runner step contracts](reference/runner-step-contracts.md)
- [Runner metadata](reference/runner-metadata.md)
- [Codex runner adapter](reference/codex-runner-adapter.md)
- [Claude runner adapter](reference/claude-runner-adapter.md)
- [Gemini runner adapter](reference/gemini-runner-adapter.md)
- [Runner preview workflows](guides/runner-preview-workflows.md)
- [Single-agent fixture loop](guides/single-agent-fixture-loop.md)
- [Agent roles](reference/agent-roles.md)
- [Adapter packages](reference/adapter-packages.md)
- [Worker results](reference/worker-results.md)

### 4 · Connecting a provider

The provider transport is independent of the runner. Use OpenAI, Anthropic, or
any OAI-compatible endpoint — including local servers like Ollama.

- [Model providers](reference/model-providers.md)
- [Provider routing](guides/provider-routing.md)
- [Provider switching](reference/provider-switching.md)
- [Provider failover](reference/provider-failover.md)
- [Provider certification](reference/provider-certification.md)
- [Authentication & credentials](guides/authentication.md)
- [Prompt compiler](reference/prompt-compiler.md)

### 5 · Connecting memory & Stigmem

Local SQLite by default; Stigmem when you need durable team-scale memory.

- [Connecting Stigmem](guides/connecting-stigmem.md)
- [Stigmem docs demo](guides/stigmem-docs-demo.md)
- [Memory backends](reference/memory-backends.md)
- [Stigmem compatibility](reference/stigmem-compatibility.md)
- [Local store](reference/local-store.md)
- [Local state](reference/local-state.md)

### 6 · CLI & configuration reference

Look here for flags, file shapes, environment variables, and CI hooks.

- [CLI reference](reference/cli.md)
- [Config reference](reference/config.md)
- [GitHub config](reference/github-config.md)
- [CI/CD](reference/ci-cd.md)

### 7 · Side effects, failure modes & recovery

What Craik does to your environment, where it draws boundaries, and what
happens when something goes wrong.

- [Side-effect wrappers](reference/side-effect-wrappers.md)
- [Failure modes](reference/failure-modes.md)
- [Recovery mode](reference/recovery.md)
- [Public boundary provenance](reference/public-boundary-provenance.md)
- [Self-audit](reference/self-audit.md)
- [Post-MVP scope](reference/post-mvp-scope.md)

### 8 · Extending with skills & plugins

Skill and plugin contracts so the runtime can grow without giving up
governance.

- [Community skills](guides/community-skills.md)
- [Community plugins](guides/community-plugins.md)
- [Skill packages](reference/skill-packages.md)
- [Skill registries](reference/skill-registries.md)
- [Skill invocation contexts](reference/skill-contexts.md)
- [Skill telemetry](reference/skill-telemetry.md)
- [Skill proposals](reference/skill-proposals.md)
- [Skill replay](reference/skill-replay.md)
- [Skill promotion gates](reference/skill-promotion-gates.md)
- [Skill rollbacks](reference/skill-rollbacks.md)
- [Plugin descriptors](reference/plugin-descriptors.md)
- [Plugin probation](reference/plugin-probation.md)
- [Plugin receipts](reference/plugin-receipts.md)
- [Plugin capability grants](reference/plugin-capability-grants.md)

### 9 · Integrations & migrations

GitHub, MCP, adjacent runtimes, and migration paths from existing tools.

- [GitHub adapter](guides/github-adapter.md)
- [MCP ecosystem compatibility](guides/mcp-ecosystem-compatibility.md)
- [MCP client](reference/mcp-client.md)
- [MCP export boundary](reference/mcp-export-boundary.md)
- [Reference integrations](reference/reference-integrations.md)
- [Adjacent runtime bridge](reference/adjacent-runtime-bridge.md)
- [Adjacent tool migration assessment](reference/adjacent-tool-migration.md)
- [Multi-agent workflow bridge](reference/multi-agent-workflow-bridge.md)
- [Multi-agent workflow migration assessment](reference/multi-agent-workflow-migration.md)
- [Import dry-run reports](reference/import-dry-run.md)
- [Migration maps](reference/migration-maps.md)

### 10 · Work-graph export

Exporting the typed graph for review, audit, or visualization.

- [Graph export](reference/graph-export.md)

## Where to go next

- **Run, monitor, and maintain** → [Operate](operate.md)
- **Govern execution** → [Secure](secure.md)
- **Understand the model** → [Learn](learn.md)
