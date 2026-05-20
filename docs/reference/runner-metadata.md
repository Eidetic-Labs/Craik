# Runner metadata

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The stable metadata snapshot every adapter records at the boundary, so
receipts and handoffs can explain which runner produced work — without
leaking provider-specific fields into the stable contract surface.

</div>

<div className="craik-keypoint">

**Descriptive, not authorizing.**

Receipt and handoff metadata is descriptive. It does not grant tool
authority, prove that external execution occurred, or replace policy
receipts for concrete side effects.

</div>

## Stable keys

<div className="craik-grid">

<div><h4><code>runner_id</code></h4></div>
<div><h4><code>runner_name</code></h4></div>
<div><h4><code>adapter</code></h4></div>
<div><h4><code>adapter_version</code></h4></div>
<div><h4><code>execution_mode</code></h4></div>
<div><h4><code>capabilities</code></h4></div>
<div><h4><code>trust_profile</code></h4></div>
<div><h4><code>capability_profile</code></h4></div>
<div><h4><code>policy_notes</code></h4></div>

</div>

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Storage</span></dt>
<dd>Where it lives</dd>
</div>

<div>
<dt>Receipt snapshot</dt>
<dt><span className="craik-fields__type">capability_receipt</span></dt>
<dd><code>craik.capability_receipt.result.metadata.runner_metadata</code></dd>
</div>

<div>
<dt>Handoff snapshot</dt>
<dt><span className="craik-fields__type">handoff</span></dt>
<dd>First unique runner snapshots on task receipts in <code>craik.handoff.runner_metadata</code>.</dd>
</div>

</div>

## Runner-specific metadata

Runner-specific details remain nested under `runner_specific`. Preview
adapters can preserve local fixture mode, live availability,
executable names, or provider-specific session metadata without
promoting those fields to the core contract.

<div className="craik-keypoint">

**Always redacted before storage.**

Runner metadata snapshots are redacted before they are stored or
copied into handoffs. Secret-like keys (tokens, passwords, API keys,
credentials) are replaced with <code>[REDACTED]</code>.

</div>

## What's next

<div className="craik-next">

<a href="runner-adapter-contract/">
<strong>Reference</strong>
<span>Runner adapter contract</span>
<small>How adapters produce and preserve this metadata.</small>
</a>

<a href="../guides/runner-preview-workflows/">
<strong>Guide</strong>
<span>Runner preview workflows</span>
<small>Smoke-test that metadata appears in outputs.</small>
</a>

<a href="../runtime-contracts/">
<strong>Read</strong>
<span>Runtime contracts</span>
<small>The wider receipt and handoff shapes this metadata attaches to.</small>
</a>

</div>
