# Budget and quota view

<p className="craik-meta"><span>2 min read</span><span>Reference · preview</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The read-only operator display for configured limits, observed usage,
missing data, exceeded limits, and notes.

</div>

<div className="craik-keypoint">

**Don't invent missing cost data.**

If a run or local store does not contain cost, token, request, or
quota information, the view shows the missing key explicitly.

</div>

## What it formats

<div className="craik-grid">

<div><h4>Configured limits</h4></div>
<div><h4>Usage summaries</h4></div>
<div><h4>Missing data</h4></div>
<div><h4>Exceeded limits</h4></div>
<div><h4>Notes</h4></div>

</div>

## Exceeded state

<div className="craik-keypoint">

**Display only, no enforcement.**

Exceeded states are only shown when supported data exists. The view
can display that a limit was exceeded, but it does not enforce limits
or mutate policy.

</div>

## What's next

<div className="craik-next">

<a href="operator-surface/">
<strong>Reference</strong>
<span>Operator surface</span>
<small>The shared TUI boundary.</small>
</a>

<a href="schemas/">
<strong>Reference</strong>
<span>Schema reference</span>
<small>Where budget-relevant records are persisted.</small>
</a>

<a href="provider-budgets/">
<strong>Reference</strong>
<span>Provider budgets</span>
<small>The pre-routing budget check this view surfaces.</small>
</a>

</div>
