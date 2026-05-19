---
id: secure
title: Secure
sidebar_label: Overview
sidebar_position: 0
description: Govern execution, manage identity and credentials, control side effects, and keep durable audit trails.
slug: /secure
---

# Secure Craik

Craik treats governance as a runtime concern. Policy envelopes, capability
grants, credential identity, redaction, and sandboxes are all addressable
objects — not advisory configuration. This section is the implementation map
for everyone responsible for the safety, identity, and audit properties of
their Craik install.

## Implementation paths

### 1 · Governance fundamentals

Start here to understand what "governance" means inside the runtime, then
configure the basic envelope you want every task to run inside.

- [Governance concept](concepts/governance.md)
- [Governance model](governance.md)
- [Capability grants](guides/capability-grants.md)
- [Scope control](guides/scope-control.md)
- [Fail-open behavior](guides/fail-open.md)

### 2 · Policy

The policy envelope is the per-run governance object. These docs cover its
shape, how to test it, and how to enforce it in CI.

- [Policy profiles](reference/policy-profiles.md)
- [Policy tests](reference/policy-tests.md)
- [Running policy tests](guides/running-policy-tests.md)

### 3 · Identity & credentials

Operator identity is OIDC. Credentials live in typed profiles, can be pooled,
rotated, and bound to policy. Every provider call is bound to both an operator
and a credential identity.

- [Authentication & credentials](guides/authentication.md)
- [ADR 0007 · Credential & identity architecture](adr/0007-credential-and-identity-architecture.md)

### 4 · Secrets, redaction & release

How secret material is stored, redacted, migrated, and how those properties are
preserved across releases.

- [Secrets](security/secrets.md)
- [Redaction](reference/redaction.md)
- [Secret migration policy](reference/secret-migration-policy.md)
- [Release process](security/release-process.md)

### 5 · Evidence & memory governance

Memory is governed too. Evidence-backed proposals, contradiction handling, and
preview surfaces keep truth from being silently overwritten.

- [Evidence & assumptions](guides/evidence-and-assumptions.md)
- [Contradiction inbox](guides/contradiction-inbox.md)
- [Memory proposals](guides/memory-proposals.md)
- [Memory diffs](guides/memory-diffs.md)
- [Memory impact preview](guides/memory-impact-preview.md)

### 6 · Sandboxing

Tool execution and side effects run inside policy-bound sandboxes. Pick the
backend that matches your trust boundary.

- [Sandbox backends](reference/sandbox-backends.md)
- [Local process backend](reference/local-process-backend.md)
- [Remote shell backend](reference/remote-shell-backend.md)
- [Docker sandbox backend](reference/docker-sandbox-backend.md)
- [Browser tool boundary](reference/browser-tool-boundary.md)
- [Environment receipts](reference/environment-receipts.md)

## Where to go next

- **Build something new** → [Build](build.md)
- **Run and inspect the system** → [Operate](operate.md)
- **Understand the model** → [Learn](learn.md)
