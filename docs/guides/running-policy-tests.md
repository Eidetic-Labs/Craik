# Running Policy Tests

<p className="craik-meta"><span>4 min read</span><span>For release engineers</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Run the Craik policy regression harness — locally and in CI — so the
governance contract stays enforced across every change. By the end you'll
know what's checked, how to read the report, and how to integrate the
gate into your release pipeline.

</div>

## The release gate

```bash title="Run the policy gate"
craik policy test
```

The command prints a JSON `craik.policy_test_report`. A passing report
exits with status code `0`. Any failed check exits non-zero and includes
the violated check's name plus a failure message.

<div className="craik-keypoint">

**Why a separate gate?**

Unit tests verify the runtime behaves; the policy gate verifies the
runtime keeps *its promises*. Different categories of failure — a
crashed function vs. a quietly widened authority — should be addressable
separately so they're addressable at all.

</div>

## What the gate checks

<div className="craik-grid">

<div>
<h4>Immutable path protection</h4>
<p>Writes to declared immutable paths require both approval metadata <em>and</em> a matching <code>repo.write.immutable</code> grant.</p>
</div>

<div>
<h4>Memory updates default to proposals</h4>
<p>Direct local memory writes without a <code>memory.write</code> grant are denied; the runtime emits a proposal instead.</p>
</div>

<div>
<h4>Trusted-local fail-open receipts</h4>
<p>When the <code>trusted-local</code> profile takes a fail-open path, the runtime seals a receipt with <code>fail_open: true</code>.</p>
</div>

<div>
<h4>Automation stays fail-closed</h4>
<p>Automation runs stop on uncertainty rather than widen authority. The stop is itself receipted.</p>
</div>

<div>
<h4>Runner grant boundaries are tracked</h4>
<p>Capability grants declared in the policy envelope are the only ones runners may exercise — boundary stays tight as runner adapters land.</p>
</div>

<div>
<h4>Redaction regressions</h4>
<p>Receipts, logs, handoffs, and case files all pass through the central redaction guard before persistence — verified on representative payload shapes.</p>
</div>

</div>

## CI usage

Run the policy gate alongside the rest of the validation sweep:

```bash title="The full pre-PR sweep"
uv run --python 3.12 --extra dev pytest
uv run --python 3.12 --extra dev ruff check .
uv run --python 3.12 --extra dev mypy
uv run --python 3.12 --extra dev craik policy test
```

In source-tree development specifically:

```bash title="Source-tree run"
uv run --python 3.12 --extra dev craik policy test
```

The Craik CI workflow runs this same command on every PR. **If the
policy gate fails, the PR cannot merge** — by design.

## Reading the report

`craik policy test --json` emits a machine-readable report. A passing
shape:

```json title="passing report"
{
  "schema": "craik.policy_test_report",
  "version": "0.1.0",
  "status": "pass",
  "checks": [
    { "name": "immutable_paths", "status": "pass" },
    { "name": "memory_proposal_default", "status": "pass" },
    { "name": "trusted_local_fail_open_receipt", "status": "pass" },
    { "name": "automation_fail_closed", "status": "pass" },
    { "name": "runner_grant_boundary", "status": "pass" },
    { "name": "redaction_regressions", "status": "pass" }
  ]
}
```

A failing report names the violated check and an `error.message` field
with the failure detail. Don't paper over failures — fix the underlying
issue and re-run.

## When to extend the gate

Add a check when:

<ol className="craik-steps">
<li>

**A new capability lands** (a new memory write path, a new sandbox
backend, a new credential transport). The gate should verify the
default posture before merging.

</li>
<li>

**A real incident reveals a missed invariant.** Don't fix the bug
without adding a regression — the gate is the institutional memory.

</li>
<li>

**A policy profile changes.** New profiles need their own pass/fail
cases.

</li>
</ol>

Don't add checks to verify "the tests pass" — that's pytest's job. The
policy gate is for *governance invariants* specifically.

## State the gate touches

The harness uses local Craik state and **may create a pending local
memory proposal** inside the selected `CRAIK_HOME`. This is intentional:
proving the proposal flow works requires creating one. If you're
sensitive about pollution, point `CRAIK_HOME` at a scratch directory:

```bash title="Sandboxed policy test"
CRAIK_HOME=/tmp/craik-policy-test craik policy test
```

## What's next

<div className="craik-next">

<a href="../reference/policy-tests.md">
<strong>Reference</strong>
<span>Policy tests</span>
<small>The full ruleset for every check the gate runs.</small>
</a>

<a href="../concepts/governance.md">
<strong>Read</strong>
<span>Governance</span>
<small>The governance surface this gate enforces.</small>
</a>

<a href="release-management.md">
<strong>Operate</strong>
<span>Release management</span>
<small>How the policy gate participates in cutting a release.</small>
</a>

</div>
