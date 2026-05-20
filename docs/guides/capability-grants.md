# Capability Grants

<p className="craik-meta"><span>5 min read</span><span>For policy operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- Why Craik refuses ambient authority and what a capability grant *is*.
- The three practical outcomes of a grant check.
- The grant shape, with a worked example.
- Which capability hooks the v0.1.0 runtime enforces today.

</div>

<div className="craik-keypoint">

**Capability grant**

An explicit, scoped permission to perform a specific capability against a
specific target. Grants compose with policy profiles: the profile sets
default posture, grants narrow that posture to what's authorized for the
current task.

</div>

## No ambient authority

Craik does not grant agents ambient authority. An agent can't "write to
the docs because it's a docs agent." Side effects require a matching
grant that names:

<ol className="craik-steps">
<li>**The capability** — `repo.write.docs`, `shell.execute`, `github.write`, `memory.write`.</li>
<li>**The target** — a path glob, a remote URI, a memory scope.</li>
<li>**The operations** — `write`, `execute`, `propose`, etc.</li>
<li>**The reason** — short, human-readable. Reviewers read this first.</li>
<li>**The approver** — the operator identity that authorized the grant.</li>
</ol>

When the check runs, there are three outcomes:

<div className="craik-fields">

<div>
<dt>Outcome</dt>
<dt><span className="craik-fields__type">Meaning</span></dt>
<dd>What the runtime does</dd>
</div>

<div>
<dt><code>allowed</code></dt>
<dt><span className="craik-fields__type">grant matches</span></dt>
<dd>Action proceeds; a receipt is sealed with the grant id.</dd>
</div>

<div>
<dt><code>denied</code></dt>
<dt><span className="craik-fields__type">no matching grant</span></dt>
<dd>Action is refused; a receipt may be sealed with <code>status: denied</code> for audit.</dd>
</div>

<div>
<dt><code>requires_approval</code></dt>
<dt><span className="craik-fields__type">approval gate</span></dt>
<dd>Denied until explicit approval metadata <em>and</em> a matching grant exist. Override metadata alone is not sufficient.</dd>
</div>

</div>

## The grant shape

```json title="grant_docs_write · repo.write.docs"
{
  "schema": "craik.capability_grant",
  "version": "0.1.0",
  "id": "grant_docs_write",
  "task_id": "task_docs",
  "capability": "repo.write.docs",
  "target": {
    "paths": ["docs/**"],
    "exclude": ["docs/adr/**"]
  },
  "operations": ["write"],
  "reason": "Documentation update for task_docs.",
  "approved_by": "user:maintainer"
}
```

Read the fields top-to-bottom. The grant is reviewable on its own — you
don't need to chase down a separate "what does this mean?" reference.

## Immutable paths: grants alone are not enough

ADR directories and other declared immutable paths are denied by default
under every profile. Writing to one requires **both**:

<div className="craik-decision">

<div>
<h4>Override metadata</h4>
<ul>
<li><code>approved_by</code> — the operator identity that authorized the override.</li>
<li><code>reason</code> — short, human-readable justification.</li>
<li>Attached at the action site, not buried in policy config.</li>
</ul>
</div>

<div>
<h4>A matching grant</h4>
<ul>
<li>Capability must be <code>repo.write.immutable</code> (not <code>repo.write.docs</code>).</li>
<li>Target must match the immutable path being changed.</li>
<li>Grant is task-scoped — it expires with the task.</li>
</ul>
</div>

</div>

This belt-and-suspenders rule is intentional. Immutable evidence is the
backbone of audit; "I forgot the grant" should not be able to overwrite an
ADR by accident.

## The four capability hooks today

<div className="craik-grid">

<div>
<h4><code>repo.write.docs</code></h4>
<p>Documentation writes to declared doc roots. Most common grant.</p>
</div>

<div>
<h4><code>repo.write.immutable</code></h4>
<p>Writes to immutable paths. Requires override metadata <em>and</em> the matching grant.</p>
</div>

<div>
<h4><code>shell.execute</code></h4>
<p>Shell command execution. Sandbox backend enforces additional restrictions.</p>
</div>

<div>
<h4><code>github.write</code></h4>
<p>GitHub side effects: PRs, issues, comments, reviews.</p>
</div>

<div>
<h4><code>memory.write</code></h4>
<p>Direct memory writes. Without this grant, runs leave proposals instead.</p>
</div>

</div>

The v0.1.0 hook layer checks whether a matching grant exists. Runtime
provider and tool-call paths call these checks **before** performing side
effects — there is no "try and fail" path that lets the side effect happen
under a denied posture.

## Denied receipts

When a check fails, Craik can produce a receipt with `status: denied`. This
is intentional — the audit trail captures attempted-and-refused actions the
same way it captures successful ones. The denied receipt names the missing
capability, the target, and the operator who would have authorized it.

`craik receipts list --status denied` gives you the queue of denied
attempts. Frequent denials in the same shape are usually a signal that the
policy envelope or grants need to widen narrowly — not that the runtime
should be looser overall.

## What's next

<div className="craik-next">

<a href="../scope-control/">
<strong>Do</strong>
<span>Scope control</span>
<small>Keep grants tight by keeping intent locks tight.</small>
</a>

<a href="../../reference/policy-profiles/">
<strong>Reference</strong>
<span>Policy profiles</span>
<small>How profiles set the default posture grants compose against.</small>
</a>

<a href="../../concepts/governance/">
<strong>Read</strong>
<span>Governance</span>
<small>The full picture: profiles, grants, immutable paths, redaction, receipts.</small>
</a>

</div>
