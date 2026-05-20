# Local process backend

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `LocalProcessRequest` boundary that represents execution through
the host process environment — and what it intentionally does not
provide.

</div>

<div className="craik-keypoint">

**Decision boundary, not ambient shell authority.**

The helper returns an allowed or denied decision that can be recorded
in receipts before the caller dispatches through a governed execution
path.

</div>

## Required controls

<div className="craik-grid">

<div><h4>Sandbox backend</h4><p>Kind <code>local_process</code> · isolation <code>process</code>.</p></div>
<div><h4>Declared <code>shell.execute</code> capability</h4><p>With <code>run</code> operation.</p></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Capability grant id</h4></div>
<div><h4>Receipt id</h4></div>
<div><h4>Redaction controls</h4><p>For persisted metadata.</p></div>

</div>

Requests missing any of those controls are denied before execution.

## Limitations

<div className="craik-keypoint">

**No container, VM, or remote isolation.**

The local process backend can only describe and authorize a command
reference for a caller that already has local execution capability.
Don't use it for untrusted commands, unreviewed input, or workloads
that require filesystem, network, or process isolation.

</div>

<div className="craik-keypoint">

**Inline shell strings are denied.**

This avoids granting broad shell authority by smuggling flags, pipes,
command substitution, or chained commands into a command reference
field.

</div>

## What's next

<div className="craik-next">

<a href="sandbox-backends/">
<strong>Reference</strong>
<span>Sandbox backends</span>
<small>The shared contract.</small>
</a>

<a href="environment-receipts/">
<strong>Reference</strong>
<span>Environment receipts</span>
<small>How allowed and denied decisions persist.</small>
</a>

<a href="docker-sandbox-backend/">
<strong>Reference</strong>
<span>Docker sandbox backend</span>
<small>The container alternative when isolation matters.</small>
</a>

</div>
