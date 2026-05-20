# Side-effect wrappers

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The MVP wrappers that pass shell, file, memory, and GitHub side
effects through policy, grant, redaction, and receipt boundaries —
plus the testing seam that keeps everything deterministic.

</div>

<div className="craik-keypoint">

**Callbacks for execution, receipts for outcomes.**

Shell and GitHub wrappers accept callbacks for the actual execution
boundary, which keeps tests deterministic and prevents ambient side
effects. Denials persist receipts; allowed actions persist
environment receipts.

</div>

## Coverage

`craik.runtime.side_effects` provides MVP wrappers for:

<div className="craik-grid">

<div><h4>Shell command references</h4></div>
<div><h4>Repository file writes</h4></div>
<div><h4>Durable memory or Stigmem fact writes</h4></div>
<div><h4>Guarded GitHub write operations</h4></div>

</div>

## Files

<div className="craik-keypoint">

**Immutable paths require approval.**

File writes use <code>check_file_write_grant</code> and
<code>DocsProfile</code> immutable path rules. Immutable paths require
approval metadata and a matching <code>repo.write.immutable</code>
grant. Written content is redacted before persistence.

</div>

## Memory

Memory writes use `memory.write` grants and a durable writer
interface. Public metadata records entity, relation, scope, and
confidence only — raw credentials or secret material must not appear
in receipts.

## GitHub

GitHub writes use `github.write` grants with explicit operations such
as `create_pr`. The wrapper records the operation and redacted result
metadata.

## What's next

<div className="craik-next">

<a href="../policy-profiles/">
<strong>Reference</strong>
<span>Policy profiles</span>
<small>The profiles every wrapper checks.</small>
</a>

<a href="../../guides/capability-grants/">
<strong>Guide</strong>
<span>Capability grants</span>
<small>How operators issue the grants wrappers verify.</small>
</a>

<a href="../redaction/">
<strong>Reference</strong>
<span>Redaction</span>
<small>The persistence boundary wrappers run through.</small>
</a>

</div>
