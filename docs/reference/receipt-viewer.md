# Receipt viewer

<p className="craik-meta"><span>2 min read</span><span>Reference · preview</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The read-only operator view over capability and plugin receipts. What
the v0.7.0 TUI surface formats, the supported outcomes, and the
inspection-only boundary.

</div>

<div className="craik-keypoint">

**Design rationale: [ADR 0005 · Receipts and handoffs as public contracts](../adr/0005-receipts-and-handoffs-as-public-contracts.md).**

</div>

## What it formats

<div className="craik-decision">

<div>
<h4>Capability receipts</h4>
<ul>
<li>Receipt id · task · actor · capability · target · policy profile</li>
<li>Status · reason · redacted summary · redaction state</li>
</ul>
</div>

<div>
<h4>Plugin receipts</h4>
<ul>
<li>Receipt id · task · actor · plugin descriptor · action · trust boundary</li>
<li>Status · redacted summary · redaction state</li>
<li>Linked capability grants · evidence · handoffs</li>
</ul>
</div>

</div>

## Outcomes

<div className="craik-grid">

<div><h4><code>passed</code></h4></div>
<div><h4><code>failed</code></h4></div>
<div><h4><code>denied</code></h4></div>
<div><h4><code>skipped</code></h4></div>

</div>

The view displays each status without expanding raw command output or
unredacted plugin output.

## Boundaries

<div className="craik-keypoint">

**Inspection only.**

The viewer does not approve grants, retry commands, rerun plugins, or
mutate receipt records.

</div>

## What's next

<div className="craik-next">

<a href="operator-surface/">
<strong>Reference</strong>
<span>Operator surface</span>
<small>The shared TUI boundary.</small>
</a>

<a href="handoff-viewer/">
<strong>Reference</strong>
<span>Handoff viewer</span>
<small>The handoff side of the receipt-handoff pair.</small>
</a>

<a href="plugin-receipts/">
<strong>Reference</strong>
<span>Plugin receipts</span>
<small>The plugin-receipt contract this viewer reads.</small>
</a>

</div>
