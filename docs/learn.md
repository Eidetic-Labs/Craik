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
[Build → Getting started](/docs/guides/installation).

## What's in this section

### 1 · The product

Start here to understand the thesis, who Craik is for, and why it is different
from agent frameworks that focus only on tool calling.

- [Vision](/docs/vision) — the long-term direction.
- [Product strategy](/docs/product-strategy) — positioning and audience.
- [Differentiators](/docs/differentiators) — what makes Craik distinct.
- [Features](/docs/features) — feature surface at a glance.
- [Architecture](/docs/architecture) — the runtime architecture.

### 2 · Core concepts

Read these in order on your first pass. Each concept maps to a typed runtime
object that the rest of the docs reference by name.

1. [Project model](/docs/concepts/project-model)
2. [Case files](/docs/concepts/case-files)
3. [Single-agent execution loop](/docs/concepts/single-agent-loop)
4. [Receipts](/docs/concepts/receipts)
5. [Handoffs](/docs/concepts/handoffs)
6. [Work graph](/docs/concepts/work-graph)
7. [Memory & Stigmem](/docs/concepts/memory-and-stigmem)
8. [Governance](/docs/concepts/governance)
9. [Intent locks](/docs/concepts/intent-locks)

### 3 · Runtime contracts

The typed objects every Craik component speaks. Read these when you need to
implement an adapter, write a policy, or interpret a receipt.

- [Runtime contracts overview](/docs/runtime-contracts)
- [Schemas](/docs/reference/schemas)
- [Project profile](/docs/reference/project-profile)
- [Run state](/docs/reference/run-state)
- [Worker results](/docs/reference/worker-results)
- [Failure modes](/docs/reference/failure-modes)

### 4 · Status & roadmap

Where Craik is today and where it is going. Honest about what's not yet built.

- [Current MVP](/docs/mvp)
- [MVP roadmap](/docs/mvp-roadmap)
- [Roadmap](/docs/roadmap)
- [Release readiness · v0.1.0](/docs/release-readiness-v0.1.0)
- [Limitations](/docs/limitations)
- [Implementation plan](/docs/implementation-plan)

### 5 · Architecture Decision Records

The reasons behind the structural choices. Stable, dated, and referenced from
the rest of the docs.

- [ADR index](/docs/adr/)
- ADR 0001 — [MVP runner scope](/docs/adr/record-mvp-runner-scope)
- ADR 0002 — [Provider transport and mode families](/docs/adr/provider-transport-and-mode-families)
- ADR 0003 — [Secret handling](/docs/adr/secret-handling)
- ADR 0004 — [Policy envelope shape](/docs/adr/policy-envelope-shape)
- ADR 0005 — [Receipts and handoffs as public contracts](/docs/adr/receipts-and-handoffs-as-public-contracts)
- ADR 0006 — [Package and runtime layout](/docs/adr/package-and-runtime-layout)
- ADR 0007 — [Credential and identity architecture](/docs/adr/credential-and-identity-architecture)

### 6 · Stigmem integration

Craik runs in degraded local mode without Stigmem, but Stigmem is the reference
substrate for team-scale memory.

- [Stigmem integration](/docs/stigmem-integration)

## Where to go next

Once the concepts are clear, choose your path:

- **Install and run something** → [Build · Getting started](/docs/guides/installation)
- **Integrate a runner or provider** → [Build · Connecting runners](/docs/reference/runner-adapter-contract)
- **Govern execution** → [Secure · Governance fundamentals](/docs/concepts/governance)
- **Run and inspect the system** → [Operate · Operator views](/docs/reference/operator-surface)
