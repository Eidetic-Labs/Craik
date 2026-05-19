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

1. [Install Craik](/docs/guides/installation)
2. [Quickstart](/docs/guides/quickstart)
3. [Register a project](/docs/guides/project-registry)

## Implementation paths

### 1 · Getting started

Install the CLI, point it at a project, and run the first governed task.

- [Installation](/docs/guides/installation)
- [Quickstart](/docs/guides/quickstart)
- [Setup wizard](/docs/guides/setup)
- [Configuring Craik home](/docs/guides/configuring-craik-home)

### 2 · Working with projects

The project profile is the durable representation of a repository. Case files
are the per-task brief built from it. Handoffs are how runs end.

- [Project registry](/docs/guides/project-registry)
- [Project profile reference](/docs/reference/project-profile)
- [Using case files](/docs/guides/using-case-files)
- [Writing handoffs](/docs/guides/writing-handoffs)

### 3 · Connecting a runner

Codex, Claude, Gemini — or your own. Every runner consumes the same contracts.

- [Runner adapter contract](/docs/reference/runner-adapter-contract)
- [Runner step contracts](/docs/reference/runner-step-contracts)
- [Runner metadata](/docs/reference/runner-metadata)
- [Codex runner adapter](/docs/reference/codex-runner-adapter)
- [Claude runner adapter](/docs/reference/claude-runner-adapter)
- [Gemini runner adapter](/docs/reference/gemini-runner-adapter)
- [Runner preview workflows](/docs/guides/runner-preview-workflows)
- [Single-agent fixture loop](/docs/guides/single-agent-fixture-loop)
- [Agent roles](/docs/reference/agent-roles)
- [Adapter packages](/docs/reference/adapter-packages)
- [Worker results](/docs/reference/worker-results)

### 4 · Connecting a provider

The provider transport is independent of the runner. Use OpenAI, Anthropic, or
any OAI-compatible endpoint — including local servers like Ollama.

- [Model providers](/docs/reference/model-providers)
- [Provider routing](/docs/guides/provider-routing)
- [Provider switching](/docs/reference/provider-switching)
- [Provider failover](/docs/reference/provider-failover)
- [Provider certification](/docs/reference/provider-certification)
- [Authentication & credentials](/docs/guides/authentication)
- [Prompt compiler](/docs/reference/prompt-compiler)

### 5 · Connecting memory & Stigmem

Local SQLite by default; Stigmem when you need durable team-scale memory.

- [Connecting Stigmem](/docs/guides/connecting-stigmem)
- [Stigmem docs demo](/docs/guides/stigmem-docs-demo)
- [Memory backends](/docs/reference/memory-backends)
- [Stigmem compatibility](/docs/reference/stigmem-compatibility)
- [Local store](/docs/reference/local-store)
- [Local state](/docs/reference/local-state)

### 6 · CLI & configuration reference

Look here for flags, file shapes, environment variables, and CI hooks.

- [CLI reference](/docs/reference/cli)
- [Config reference](/docs/reference/config)
- [GitHub config](/docs/reference/github-config)
- [CI/CD](/docs/reference/ci-cd)

### 7 · Side effects, failure modes & recovery

What Craik does to your environment, where it draws boundaries, and what
happens when something goes wrong.

- [Side-effect wrappers](/docs/reference/side-effect-wrappers)
- [Failure modes](/docs/reference/failure-modes)
- [Recovery mode](/docs/reference/recovery)
- [Public boundary provenance](/docs/reference/public-boundary-provenance)
- [Self-audit](/docs/reference/self-audit)
- [Post-MVP scope](/docs/reference/post-mvp-scope)

### 8 · Extending with skills & plugins

Skill and plugin contracts so the runtime can grow without giving up
governance.

- [Community skills](/docs/guides/community-skills)
- [Community plugins](/docs/guides/community-plugins)
- [Skill packages](/docs/reference/skill-packages)
- [Skill registries](/docs/reference/skill-registries)
- [Skill invocation contexts](/docs/reference/skill-contexts)
- [Skill telemetry](/docs/reference/skill-telemetry)
- [Skill proposals](/docs/reference/skill-proposals)
- [Skill replay](/docs/reference/skill-replay)
- [Skill promotion gates](/docs/reference/skill-promotion-gates)
- [Skill rollbacks](/docs/reference/skill-rollbacks)
- [Plugin descriptors](/docs/reference/plugin-descriptors)
- [Plugin probation](/docs/reference/plugin-probation)
- [Plugin receipts](/docs/reference/plugin-receipts)
- [Plugin capability grants](/docs/reference/plugin-capability-grants)

### 9 · Integrations & migrations

GitHub, MCP, adjacent runtimes, and migration paths from existing tools.

- [GitHub adapter](/docs/guides/github-adapter)
- [MCP ecosystem compatibility](/docs/guides/mcp-ecosystem-compatibility)
- [MCP client](/docs/reference/mcp-client)
- [MCP export boundary](/docs/reference/mcp-export-boundary)
- [Reference integrations](/docs/reference/reference-integrations)
- [Adjacent runtime bridge](/docs/reference/adjacent-runtime-bridge)
- [Adjacent tool migration assessment](/docs/reference/adjacent-tool-migration)
- [Multi-agent workflow bridge](/docs/reference/multi-agent-workflow-bridge)
- [Multi-agent workflow migration assessment](/docs/reference/multi-agent-workflow-migration)
- [Import dry-run reports](/docs/reference/import-dry-run)
- [Migration maps](/docs/reference/migration-maps)

### 10 · Work-graph export

Exporting the typed graph for review, audit, or visualization.

- [Graph export](/docs/reference/graph-export)

## Where to go next

- **Run, monitor, and maintain** → [Operate](/docs/operate)
- **Govern execution** → [Secure](/docs/secure)
- **Understand the model** → [Learn](/docs/learn)
