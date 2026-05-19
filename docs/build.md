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

### 1 · Getting started

Install the CLI, point it at a project, and run the first governed task.

- [Installation](guides/installation.md)
- [Quickstart](guides/quickstart.md)
- [Setup wizard](guides/setup.md)
- [Configuring Craik home](guides/configuring-craik-home.md)

### 2 · Working with projects

The project profile is the durable representation of a repository. Case files
are the per-task brief built from it. Handoffs are how runs end.

- [Project registry](guides/project-registry.md)
- [Project profile reference](reference/project-profile.md)
- [Using case files](guides/using-case-files.md)
- [Writing handoffs](guides/writing-handoffs.md)

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
