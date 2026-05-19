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

- [Governance concept](/docs/concepts/governance)
- [Governance model](/docs/governance)
- [Capability grants](/docs/guides/capability-grants)
- [Scope control](/docs/guides/scope-control)
- [Fail-open behavior](/docs/guides/fail-open)

### 2 · Policy

The policy envelope is the per-run governance object. These docs cover its
shape, how to test it, and how to enforce it in CI.

- [Policy profiles](/docs/reference/policy-profiles)
- [Policy tests](/docs/reference/policy-tests)
- [Running policy tests](/docs/guides/running-policy-tests)

### 3 · Identity & credentials

Operator identity is OIDC. Credentials live in typed profiles, can be pooled,
rotated, and bound to policy. Every provider call is bound to both an operator
and a credential identity.

- [Authentication & credentials](/docs/guides/authentication)
- [ADR 0007 · Credential & identity architecture](/docs/adr/credential-and-identity-architecture)

### 4 · Secrets, redaction & release

How secret material is stored, redacted, migrated, and how those properties are
preserved across releases.

- [Secrets](/docs/security/secrets)
- [Redaction](/docs/reference/redaction)
- [Secret migration policy](/docs/reference/secret-migration-policy)
- [Release process](/docs/security/release-process)

### 5 · Evidence & memory governance

Memory is governed too. Evidence-backed proposals, contradiction handling, and
preview surfaces keep truth from being silently overwritten.

- [Evidence & assumptions](/docs/guides/evidence-and-assumptions)
- [Contradiction inbox](/docs/guides/contradiction-inbox)
- [Memory proposals](/docs/guides/memory-proposals)
- [Memory diffs](/docs/guides/memory-diffs)
- [Memory impact preview](/docs/guides/memory-impact-preview)

### 6 · Sandboxing

Tool execution and side effects run inside policy-bound sandboxes. Pick the
backend that matches your trust boundary.

- [Sandbox backends](/docs/reference/sandbox-backends)
- [Local process backend](/docs/reference/local-process-backend)
- [Remote shell backend](/docs/reference/remote-shell-backend)
- [Docker sandbox backend](/docs/reference/docker-sandbox-backend)
- [Browser tool boundary](/docs/reference/browser-tool-boundary)
- [Environment receipts](/docs/reference/environment-receipts)

## Where to go next

- **Build something new** → [Build](/docs/build)
- **Run and inspect the system** → [Operate](/docs/operate)
- **Understand the model** → [Learn](/docs/learn)
