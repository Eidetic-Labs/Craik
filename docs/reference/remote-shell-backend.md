# Remote shell backend

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The auditable boundary for SSH or equivalent remote command execution
— the target record, required controls, and security boundary.

</div>

<div className="craik-keypoint">

**Boundary, not connection.**

The helper does not open connections or execute commands. It records
and evaluates a decision.

</div>

## Target

`RemoteShellTarget` stores non-secret target metadata:

<div className="craik-grid">

<div><h4>Host reference</h4></div>
<div><h4>Optional user &amp; port references</h4></div>
<div><h4>External auth reference name</h4></div>
<div><h4>Non-secret metadata</h4></div>

</div>

<div className="craik-keypoint">

**References, not values.**

References point to configuration or secret tooling — never raw
usernames with passwords, bearer tokens, SSH private keys, or
credential values.

</div>

## Required controls

<div className="craik-grid">

<div><h4>Sandbox backend</h4><p>Kind <code>remote_shell</code> · isolation <code>remote</code>.</p></div>
<div><h4>Declared <code>shell.remote.execute</code> capability</h4><p>With <code>run</code> operation.</p></div>
<div><h4>Remote target id</h4></div>
<div><h4>External auth reference name</h4></div>
<div><h4>Policy envelope id</h4></div>
<div><h4>Capability grant id</h4></div>
<div><h4>Receipt id</h4></div>
<div><h4>Redaction controls</h4><p>For persisted metadata.</p></div>

</div>

Denied and allowed decisions preserve the backend id, target id,
command reference, receipt id when present, decision reason, and
required controls.

## Security boundary

<div className="craik-keypoint">

**Command references, not inline strings.**

Inline SSH commands, pipes, chained commands, and command substitution
are denied before dispatch. Remote shell backends should be used only
for trusted, policy-approved targets. They do not provide container
isolation, local filesystem protection, network egress filtering, or
credential brokering.

</div>

Store SSH keys, passwords, tokens, and host secrets outside Craik
configuration and refer to them by auth reference name.

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
<small>The audit trail for remote decisions.</small>
</a>

<a href="docker-sandbox-backend/">
<strong>Reference</strong>
<span>Docker sandbox backend</span>
<small>The container alternative when isolation matters.</small>
</a>

</div>
