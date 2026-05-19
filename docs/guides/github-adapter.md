# GitHub adapter

<p className="craik-meta"><span>2 min read</span><span>For operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Use the read-only GitHub adapter to load repo metadata, issues, PRs,
and commit-status into case files. Writes are not part of the MVP
adapter.

</div>

<div className="craik-keypoint">

**Read-only by design.**

GitHub writes (issues · comments · branches · PRs) require future
guarded write workflows and explicit capability grants. The shipped
adapter never writes.

</div>

## What the adapter reads

<div className="craik-grid">

<div><h4>Repository metadata</h4></div>
<div><h4>Open issues</h4></div>
<div><h4>Open pull requests</h4></div>
<div><h4>Changed files for open PRs</h4></div>
<div><h4>Commit status for local <code>HEAD</code></h4></div>

</div>

## Build a case file

<div className="craik-fields">

<div>
<dt>Mode</dt>
<dt><span className="craik-fields__type">Command</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt>With GitHub context</dt>
<dt><span className="craik-fields__type">default</span></dt>
<dd><code>craik case build task_review_docs</code></dd>
</div>

<div>
<dt>Without GitHub network access</dt>
<dt><span className="craik-fields__type">offline</span></dt>
<dd><code>craik case build task_review_docs --no-github</code></dd>
</div>

</div>

GitHub context is stored in the case file `github_state` field. If the
project remote is not a GitHub repository, the API is unavailable,
auth fails, or rate limits block reads, Craik records a warning and
leaves an assumption instead of failing the case-file build.

## What's next

<div className="craik-next">

<a href="../using-case-files/">
<strong>Guide</strong>
<span>Using case files</span>
<small>Read the assembled case file and inspect the <code>github_state</code> section.</small>
</a>

<a href="../../reference/github-config/">
<strong>Reference</strong>
<span>GitHub config</span>
<small>Token, scopes, and rate-limit posture.</small>
</a>

<a href="../capability-grants/">
<strong>Guide</strong>
<span>Capability grants</span>
<small>Why GitHub writes require grants and how the workflow will compose.</small>
</a>

</div>
