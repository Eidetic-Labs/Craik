# Policy profiles

<p className="craik-meta"><span>3 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The three shipped v0.1.0 policy profiles — strict, trusted-local,
automation — what each allows by default, how to preview them, and
how to run the regression gate.

</div>

<div className="craik-keypoint">

**Design rationale: [ADR 0004 · Policy envelope shape](../adr/0004-policy-envelope-shape.md).**

</div>

## Every envelope includes

<div className="craik-grid">

<div><h4>Profile name</h4></div>
<div><h4>Fail-open status</h4></div>
<div><h4>Allowed capabilities</h4></div>
<div><h4>Denied capabilities</h4></div>
<div><h4>Approval requirements</h4></div>
<div><h4>Verification requirements</h4></div>
<div><h4>Receipt requirement</h4></div>
<div><h4>Handoff requirement</h4></div>
<div><h4>Redaction requirement</h4></div>

</div>

## Strict

`strict` is the default profile.

<div className="craik-fields">

<div>
<dt>Property</dt>
<dt><span className="craik-fields__type">Default</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt>Fail-open</dt>
<dt><span className="craik-fields__type">disabled</span></dt>
<dd></dd>
</div>

<div>
<dt>Repository &amp; memory read</dt>
<dt><span className="craik-fields__type">allowed</span></dt>
<dd>Read-only.</dd>
</div>

<div>
<dt>Receipts</dt>
<dt><span className="craik-fields__type">required</span></dt>
<dd></dd>
</div>

<div>
<dt>Redaction</dt>
<dt><span className="craik-fields__type">required</span></dt>
<dd></dd>
</div>

<div>
<dt>Writes · shell · GitHub writes · direct memory writes</dt>
<dt><span className="craik-fields__type">grant required</span></dt>
<dd>Explicit grants only.</dd>
</div>

<div>
<dt>Immutable path writes</dt>
<dt><span className="craik-fields__type">denied</span></dt>
<dd></dd>
</div>

</div>

Preview:

```sh
craik policy show
```

## Trusted-local

<div className="craik-keypoint">

**Never selected accidentally.**

`trusted-local` is an explicit fail-open profile for trusted local
development. Callers must opt in.

</div>

```sh
craik policy show --profile trusted-local --trusted-local-fail-open
```

<div className="craik-fields">

<div>
<dt>Property</dt>
<dt><span className="craik-fields__type">Default</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt>Fail-open</dt>
<dt><span className="craik-fields__type">enabled</span></dt>
<dd>Every fail-open decision creates a receipt.</dd>
</div>

<div>
<dt>Local file &amp; shell</dt>
<dt><span className="craik-fields__type">may be broader</span></dt>
<dd>Compared to strict.</dd>
</div>

<div>
<dt>Receipts &amp; redaction</dt>
<dt><span className="craik-fields__type">required</span></dt>
<dd>Unchanged.</dd>
</div>

<div>
<dt>Immutable path writes</dt>
<dt><span className="craik-fields__type">denied</span></dt>
<dd>Unless separately approved.</dd>
</div>

<div>
<dt>Direct memory writes</dt>
<dt><span className="craik-fields__type">approval required</span></dt>
<dd></dd>
</div>

</div>

Trusted-local does not bypass immutable path protection. Immutable
writes still require explicit override metadata and a matching
immutable write grant.

## Automation

`automation` is for CI and unattended workflows.

<div className="craik-fields">

<div>
<dt>Property</dt>
<dt><span className="craik-fields__type">Default</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt>Fail-open</dt>
<dt><span className="craik-fields__type">disabled</span></dt>
<dd></dd>
</div>

<div>
<dt>Approval prompts</dt>
<dt><span className="craik-fields__type">not required</span></dt>
<dd></dd>
</div>

<div>
<dt>Failures</dt>
<dt><span className="craik-fields__type">stop</span></dt>
<dd>Stop execution instead of widening authority.</dd>
</div>

<div>
<dt>Broad shell</dt>
<dt><span className="craik-fields__type">denied</span></dt>
<dd></dd>
</div>

<div>
<dt>Direct memory writes</dt>
<dt><span className="craik-fields__type">denied</span></dt>
<dd>Unless granted elsewhere.</dd>
</div>

</div>

Preview:

```sh
craik policy show --profile automation
```

## Visibility

<div className="craik-keypoint">

**Fail-open is always traceable.**

Fail-open profile use is visible in the policy envelope immediately
and is preserved in case files, receipts, and handoffs.

</div>

Capability grants are evaluated separately from profile generation.
Profiles define default allowed, denied, approval, and verification
sets; grants authorize specific side-effect requests.

## Regression gate

Run before release-sensitive changes:

```sh
craik policy test
```

The gate verifies:

<div className="craik-grid">

<div><h4>Immutable path protection</h4></div>
<div><h4>Memory proposal defaults</h4></div>
<div><h4>Trusted-local fail-open receipts</h4></div>
<div><h4>Automation fail-closed behavior</h4></div>
<div><h4>Runner grant boundary tracking</h4></div>
<div><h4>Redaction</h4><p>For policy-relevant payload shapes.</p></div>

</div>

## What's next

<div className="craik-next">

<a href="../adr/policy-envelope-shape/">
<strong>ADR</strong>
<span>0004 · Policy envelope shape</span>
<small>Design rationale for the envelope contract.</small>
</a>

<a href="../guides/fail-open/">
<strong>Guide</strong>
<span>Fail-open</span>
<small>How trusted-local opt-in works in practice.</small>
</a>

<a href="../guides/running-policy-tests/">
<strong>Guide</strong>
<span>Running policy tests</span>
<small>The regression-gate workflow.</small>
</a>

</div>
