# Fail-Open

<p className="craik-meta"><span>4 min read</span><span>For policy operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- The default Craik posture: fail-closed.
- When fail-open is allowed, and what's still enforced when it is.
- How to preview a fail-open policy envelope and inspect the matching receipt.
- The boundaries fail-open never crosses.

</div>

<div className="craik-keypoint">

**Default posture: fail-closed**

When Craik can't enforce a guarantee — missing credential, unreachable
provider, ambiguous policy — it **stops**. The runtime never widens its
permissions to keep a run going. Fail-open is a narrow, named exception
that operators opt into deliberately.

</div>

## Why fail-closed is the default

Agent runtimes that quietly continue when guarantees aren't met end up
producing receipts, handoffs, and writes that *look* identical to a clean
run. That's the worst possible failure mode: you can't tell from the
artifacts whether the system was actually governed.

Craik picks the other side. If the credential profile is unreachable, the
run halts with a structured error and a receipt that names what was missing.
The next operator inherits clear state instead of an invisible degradation.

## Fail-open is profile-gated

In v0.1.0, the **only** fail-open profile is `trusted-local`. It exists
for tightly-scoped local development where the operator is the only actor
and the run can't reach external resources. It must be requested explicitly
on every run that uses it — Craik never selects it automatically.

```bash title="Preview a trusted-local envelope"
craik policy show --profile trusted-local --trusted-local-fail-open
```

This prints the resolved policy envelope without applying it. Use it as
the first step in any conversation about whether to grant fail-open access
for a specific task.

## The mandatory receipt preview

Fail-open paths always produce a receipt. Always. Preview the receipt
shape alongside the envelope before you authorize a run:

```bash title="Envelope + receipt preview"
craik policy show \
  --profile trusted-local \
  --trusted-local-fail-open \
  --include-receipt
```

The receipt records that the run took a fail-open path, names the
operator and credential identity, and is queryable later by both
`--task-id` and `--policy-id`. There is no silent fail-open.

## What fail-open does **not** bypass

Even under `trusted-local`, the runtime still enforces:

<div className="craik-grid">

<div>
<h4>Redaction</h4>
<p>Receipts continue to pass through the central redaction guard. Secrets never leak into the receipt store, fail-open or otherwise.</p>
</div>

<div>
<h4>Receipts</h4>
<p>Every receiptable action still produces a receipt. The <code>fail_open</code> flag is set to <code>true</code> so the path is auditable after the fact.</p>
</div>

<div>
<h4>Immutable paths</h4>
<p>Edits to ADR directories and other immutable evidence remain forbidden. Fail-open is about *availability*, not about widening write authority.</p>
</div>

<div>
<h4>Direct memory write approvals</h4>
<p>Direct writes to Stigmem or any memory backend still require the explicit approval flow. Fail-open does not promote memory proposals to facts.</p>
</div>

</div>

## Automation mode is always fail-closed

When Craik is invoked under automation (CI, scheduled gateway runs,
webhook ingress), it operates in a strict fail-closed posture. Automation
runs must stop on uncertainty rather than widen permissions — there is no
operator at the keyboard to authorize a fail-open path.

If your automation workflow is hitting fail-closed exits frequently, that's
signal: either the credential profile is unstable, the policy is too tight,
or the workflow needs a human review step before it touches the affected
capability. Fail-open is not the fix.

## A pragmatic checklist

Before authorizing a fail-open run, confirm:

<ol className="craik-steps">
<li>

**The task is genuinely local and bounded.** No external network calls,
no shared state, no production data.

</li>
<li>

**You can identify the operator.** Fail-open receipts are bound to OIDC
operator identity — the run isn't anonymous.

</li>
<li>

**You'll review the receipt afterward.** Don't authorize a fail-open run
and forget about it. `craik receipts list --policy-id ...` is your audit
trail.

</li>
<li>

**There isn't a cleaner fix.** If you find yourself reaching for fail-open
repeatedly, the policy envelope or credential profile probably needs to
change instead.

</li>
</ol>

## What's next

<div className="craik-next">

<a href="../reference/policy-profiles.md">
<strong>Reference</strong>
<span>Policy profiles</span>
<small>Every profile Craik ships and what it gates.</small>
</a>

<a href="capability-grants.md">
<strong>Do</strong>
<span>Capability grants</span>
<small>How to narrow what a runner can do without reaching for fail-open.</small>
</a>

<a href="../concepts/governance.md">
<strong>Read</strong>
<span>Governance</span>
<small>Why policy is a runtime object, and how all of this composes.</small>
</a>

</div>
