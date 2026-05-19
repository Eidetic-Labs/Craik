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

### 1 · The product

Start here to understand the thesis, who Craik is for, and why it is different
from agent frameworks that focus only on tool calling.

- [Vision](vision.md) — the long-term direction.
- [Product strategy](product-strategy.md) — positioning and audience.
- [Differentiators](differentiators.md) — what makes Craik distinct.
- [Features](features.md) — feature surface at a glance.
- [Architecture](architecture.md) — the runtime architecture.

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
