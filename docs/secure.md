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

<header className="craik-section-banner">
<div className="craik-section-banner__num" aria-hidden="true">01</div>
<div className="craik-section-banner__body">
<p className="craik-section-banner__kicker">Governance fundamentals</p>
<h3 className="craik-section-banner__title">
Policy is <em>part of the runtime contract.</em>
</h3>
<p className="craik-section-banner__lede">
Start here to understand what "governance" means inside the runtime,
then configure the basic envelope you want every task to run inside.
Five docs cover the concept, the runtime model, the grant surface,
the scope-control flow, and the narrow fail-open exception.
</p>
</div>
</header>

<div className="craik-product-spread">

<a className="craik-product-feature" href="concepts/governance.md">
<div>
<p className="craik-product-feature__num">Concept · 01</p>
<h4 className="craik-product-feature__title">Governance</h4>
<p className="craik-product-feature__summary">
The governance surface Craik enforces — policy profiles, capability
grants, immutable paths, fail-open visibility, receipts, redaction,
memory-proposal defaults, and the policy regression gate. Strict by
default; trusted-local is opt-in; automation is fail-closed.
</p>
<ul className="craik-product-feature__topics">
<li>policy profiles</li>
<li>capability grants</li>
<li>immutable paths</li>
<li>release gate</li>
</ul>
<span className="craik-product-feature__cta">Read the concept</span>
</div>
<blockquote className="craik-product-feature__quote">
<p className="craik-product-feature__quote-eyebrow">Runtime-native</p>
<p className="craik-product-feature__quote-text">
Craik should be governance-native. Policy is not an enterprise add-on;
it is part of the runtime contract.
</p>
<p className="craik-product-feature__quote-attribution">— Governance model · §Intro</p>
</blockquote>
</a>

</div>

<ol className="craik-adr-grid">

<li>
<a className="craik-adr-card" href="governance.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">02</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Model</span>
</div>
<h4 className="craik-adr-card__title">Governance model</h4>
<p className="craik-adr-card__decision">
The top-level statement of intent: Craik must be governance-native,
not an enterprise add-on. Policy travels with every run, every grant
is typed, every immutable boundary is enforced.
</p>
<span className="craik-adr-card__cta">Read</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="guides/capability-grants.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">03</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Grants</span>
</div>
<h4 className="craik-adr-card__title">Capability grants</h4>
<p className="craik-adr-card__decision">
Side effects require explicit, scoped grants — no ambient authority.
Three practical outcomes: allowed, denied, or requires_approval. The
v0.1 runtime enforces four capability hooks today.
</p>
<span className="craik-adr-card__cta">Guide</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="guides/scope-control.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">04</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Scope</span>
</div>
<h4 className="craik-adr-card__title">Scope control</h4>
<p className="craik-adr-card__decision">
The six intent-lock knobs (<code>accepted_interpretation</code>,
<code>in-scope</code>, <code>out-of-scope</code>, allowed autonomy,
stop conditions, scope-change rules) plus the mid-run update flow.
</p>
<span className="craik-adr-card__cta">Guide</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="guides/fail-open.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">05</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Exception</span>
</div>
<h4 className="craik-adr-card__title">Fail-open behavior</h4>
<p className="craik-adr-card__decision">
Default is fail-closed. Fail-open is profile-gated, opt-in only, and
never bypasses redaction, receipts, immutable paths, or memory-write
approvals. Automation is always fail-closed.
</p>
<span className="craik-adr-card__cta">Guide</span>
</a>
</li>

</ol>

<header className="craik-section-banner">
<div className="craik-section-banner__num" aria-hidden="true">02</div>
<div className="craik-section-banner__body">
<p className="craik-section-banner__kicker">Policy</p>
<h3 className="craik-section-banner__title">
The policy envelope — <em>per-run governance object.</em>
</h3>
<p className="craik-section-banner__lede">
Three docs cover the policy contract: the named profiles Craik ships,
the regression-test harness that verifies the profile contract, and
the operator workflow for running it locally and in CI.
</p>
</div>
</header>

<div className="craik-product-spread">

<a className="craik-product-feature" href="reference/policy-profiles.md">
<div>
<p className="craik-product-feature__num">Profiles · 01</p>
<h4 className="craik-product-feature__title">Policy profiles</h4>
<p className="craik-product-feature__summary">
The named profiles Craik ships — <code>strict</code> (default),
<code>trusted-local</code> (opt-in fail-open), and <code>automation</code>
(strict-but-headless). Design rationale lives in
<a href="adr/policy-envelope-shape/">ADR 0004</a>.
</p>
<ul className="craik-product-feature__topics">
<li>strict default</li>
<li>trusted-local</li>
<li>automation</li>
<li>ADR 0004</li>
</ul>
<span className="craik-product-feature__cta">Read profiles</span>
</div>
<blockquote className="craik-product-feature__quote">
<p className="craik-product-feature__quote-eyebrow">Design rationale</p>
<p className="craik-product-feature__quote-text">
Design rationale: ADR 0004 Policy Envelope Shape — actor, task,
profile, grant requirements, redaction posture, and receipt
obligations all bound into one typed record.
</p>
<p className="craik-product-feature__quote-attribution">— Policy profiles · §Intro</p>
</blockquote>
</a>

</div>

<ol className="craik-adr-grid">

<li>
<a className="craik-adr-card" href="reference/policy-tests.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">02</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Gate</span>
</div>
<h4 className="craik-adr-card__title">Policy tests</h4>
<p className="craik-adr-card__decision">
<code>craik policy test</code> is the machine-readable policy
regression gate for v0.1. Exits non-zero on any violated check and
prints a structured <code>craik.policy_test_report</code>.
</p>
<span className="craik-adr-card__cta">Reference</span>
</a>
</li>

<li>
<a className="craik-adr-card" href="guides/running-policy-tests.md">
<div className="craik-adr-card__head">
<span className="craik-adr-card__num">03</span>
<span className="craik-adr-card__status craik-adr-card__status--type">Operator</span>
</div>
<h4 className="craik-adr-card__title">Running policy tests</h4>
<p className="craik-adr-card__decision">
How operators and release engineers run the policy gate locally
and in CI — what each of the six checks covers, how to extend the
suite, and where the harness touches local state.
</p>
<span className="craik-adr-card__cta">Guide</span>
</a>
</li>

</ol>

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
