# Policy test reference

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

`craik policy test` — the machine-readable policy regression gate for
v0.1.0. The output shape, each result field, the shipped checks, and
the failure behavior.

</div>

<div className="craik-keypoint">

**Exit 1 on any failure.**

If any check fails, <code>status</code> becomes <code>failed</code>,
the failed result includes the violated condition, and the CLI exits
with status code <code>1</code>.

</div>

## Output shape

```json
{
  "schema": "craik.policy_test_report",
  "version": "0.1.0",
  "status": "passed",
  "summary": {
    "passed": 6,
    "failed": 0,
    "total": 6
  },
  "results": []
}
```

## Per-result fields

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Values</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>name</code></dt>
<dt><span className="craik-fields__type">stable</span></dt>
<dd>Stable check name.</dd>
</div>

<div>
<dt><code>status</code></dt>
<dt><span className="craik-fields__type"><code>passed</code> / <code>failed</code></span></dt>
<dd>Per-check result.</dd>
</div>

<div>
<dt><code>message</code></dt>
<dt><span className="craik-fields__type">prose</span></dt>
<dd>Human-readable result or failure.</dd>
</div>

<div>
<dt><code>details</code></dt>
<dt><span className="craik-fields__type">object</span></dt>
<dd>Check-specific evidence.</dd>
</div>

</div>

## Shipped checks

| Check | Purpose |
| --- | --- |
| `immutable_path_requires_override_and_grant` | Immutable paths cannot be written with ordinary docs grants. |
| `memory_writes_become_proposals` | Memory updates follow the proposal path; direct local writes are denied. |
| `trusted_local_fail_open_receipts` | Trusted-local fail-open is explicit and receipt-backed. |
| `automation_fails_closed` | Automation does not widen authority or prompt for approvals. |
| `provider_runner_enforces_shell_grants` | The provider-backed runner blocks fixture side effects without a shell grant and completes with the scoped grant. |
| `redaction_receipts_logs_handoffs_case_files` | Policy-relevant payload shapes redact secret-like material. |

## What's next

<div className="craik-next">

<a href="policy-profiles/">
<strong>Reference</strong>
<span>Policy profiles</span>
<small>The profiles each check exercises.</small>
</a>

<a href="../guides/running-policy-tests/">
<strong>Guide</strong>
<span>Running policy tests</span>
<small>How operators invoke the gate.</small>
</a>

<a href="../adr/policy-envelope-shape/">
<strong>ADR</strong>
<span>0004 · Policy envelope shape</span>
<small>The envelope contract these checks verify.</small>
</a>

</div>
