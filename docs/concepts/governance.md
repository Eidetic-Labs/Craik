# Governance

<p className="craik-meta"><span>6 min read</span><span>Core concept</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- The governance surface Craik enforces — policy profiles, grants,
  immutable paths, redaction, receipts, memory defaults.
- What strict, trusted-local, and automation profiles guarantee.
- How the policy gate verifies all of this in CI.

</div>

<div className="craik-keypoint">

**Governance**

The runtime layer that decides, *for every task*, what an agent may read,
what it may change, which actions need approval, and which actions must
leave a receipt.

Craik treats governance as a typed runtime object — not advisory
configuration. Policy envelopes, capability grants, and immutable paths
are first-class records that participate in case files, handoffs, and the
work graph.

</div>

## The v0.1.0 governance surface

<div className="craik-grid">

<div>
<h4>Policy profiles</h4>
<p>Named bundles of defaults — <code>strict</code>, <code>trusted-local</code>, <code>automation</code> — that set the posture for a run.</p>
</div>

<div>
<h4>Capability grants</h4>
<p>Explicit, time-bound permissions to perform a specific capability against a specific target.</p>
</div>

<div>
<h4>Immutable path protection</h4>
<p>ADR directories and other declared evidence paths can be read and cited, never normally edited.</p>
</div>

<div>
<h4>Fail-open visibility</h4>
<p>Fail-open paths are profile-gated and always produce receipts. There is no silent fail-open.</p>
</div>

<div>
<h4>Receipt requirements</h4>
<p>Provider calls, credential use, memory writes, and policy decisions all produce receipts.</p>
</div>

<div>
<h4>Redaction requirements</h4>
<p>Every persisted receipt and handoff passes through the central redaction guard before storage.</p>
</div>

<div>
<h4>Memory proposal defaults</h4>
<p>Agent memory updates default to proposals — never direct writes — unless a <code>memory.write</code> grant exists.</p>
</div>

<div>
<h4>Policy regression tests</h4>
<p>The policy contract is itself tested every CI run via <code>craik policy test</code>.</p>
</div>

</div>

## The three policy profiles

<div className="craik-fields">

<div>
<dt>Profile</dt>
<dt><span className="craik-fields__type">Posture</span></dt>
<dd>When to use it</dd>
</div>

<div>
<dt><code>strict</code></dt>
<dt><span className="craik-fields__type">fail-closed</span></dt>
<dd>The default. Allows read-oriented context assembly and receipt writing. Denies file writes, shell execution, GitHub writes, and direct memory writes unless a matching grant exists.</dd>
</div>

<div>
<dt><code>trusted-local</code></dt>
<dt><span className="craik-fields__type">fail-open · opt-in</span></dt>
<dd>For tightly-scoped local development. Can fail open <em>only</em> when explicitly requested. Even then, redaction, receipts, immutable path protection, and memory-write approvals are still enforced.</dd>
</div>

<div>
<dt><code>automation</code></dt>
<dt><span className="craik-fields__type">fail-closed</span></dt>
<dd>For CI and unattended workflows. Stops rather than widens authority. There is no operator at the keyboard to authorize a fail-open path.</dd>
</div>

</div>

### Strict by default

The runtime picks `strict` whenever a task doesn't ask for something
different. This means:

<ul>
<li><strong>Reads are broad.</strong> Repository files, public docs, ADRs, configured memory facts, and read-only GitHub state all flow into case files.</li>
<li><strong>Writes are denied.</strong> File edits, shell execution, GitHub writes, and direct memory writes require explicit grants.</li>
<li><strong>Receipts are mandatory.</strong> Provider calls and other governed actions produce receipts the operator can audit.</li>
</ul>

### Trusted-local is narrow on purpose

`trusted-local` exists to make local development workable without giving
up the rest of the governance surface. See [Fail-open](../guides/fail-open.md)
for the full authorization checklist and the boundaries it never crosses.

### Automation is for machines

Use `automation` for any run where there isn't an operator standing by:
CI, scheduled gateway runs, webhook ingress. When automation can't proceed,
it stops — and writes a receipt that says why. Never widens authority.

## The release gate

`craik policy test` is the regression harness for the entire governance
contract. It runs on every PR and verifies:

<ol className="craik-steps">
<li>

**Immutable path protection.** Edits to ADR directories and other
declared immutable paths are rejected, regardless of profile.

</li>
<li>

**Proposal-first memory writes.** Without a `memory.write` grant, every
agent-initiated memory update becomes a `craik.memory_proposal`.

</li>
<li>

**Trusted-local fail-open receipts.** When `trusted-local` takes a
fail-open path, a receipt with `fail_open: true` is sealed.

</li>
<li>

**Automation fail-closed behavior.** Automation runs stop rather than
widen permissions, and the stop is itself receipted.

</li>
<li>

**Runner grant boundary tracking.** Capability grants declared in the
policy envelope are the only ones runners may exercise.

</li>
<li>

**Redaction for policy-relevant payload shapes.** Receipts and handoffs
that touch credentials, tokens, or credential-bearing URLs are scrubbed
before persistence.

</li>
</ol>

## Where governance lives in the run

```text
project → policy_envelope → case_file → runner → receipt → handoff
                ▲                        │
                └─ grants the actions ───┘
```

Every governed action references the envelope it ran under. Every receipt
names the envelope id. Every handoff references the receipts. The result
is one audit trail you can walk forwards or backwards.

## What's next

<div className="craik-next">

<a href="../reference/policy-profiles.md">
<strong>Reference</strong>
<span>Policy profiles</span>
<small>The full ruleset for every profile Craik ships.</small>
</a>

<a href="../guides/capability-grants.md">
<strong>Do</strong>
<span>Add capability grants</span>
<small>Narrow, time-bound permissions that compose with strict.</small>
</a>

<a href="../reference/policy-tests.md">
<strong>Reference</strong>
<span>Policy tests</span>
<small>How the policy gate enforces the governance contract.</small>
</a>

</div>
