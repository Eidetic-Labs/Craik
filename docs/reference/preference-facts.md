# Preference facts

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `PreferenceFact` record — how Craik models user and team
preferences as reviewable records, never as silently-approved facts.

</div>

<div className="craik-keypoint">

**Inferred preferences are not approved.**

Inferred preferences must cite evidence, receipts, and inferred-from
references, and they must not include review fields.

</div>

## Fields

<div className="craik-grid">

<div><h4>Preference id</h4></div>
<div><h4>Subject</h4><p>E.g. <code>user:maintainer</code> · <code>team:platform</code>.</p></div>
<div><h4>Scope</h4><p><code>user</code> or <code>team</code>.</p></div>
<div><h4>Preference statement</h4></div>
<div><h4>Status</h4><p><code>inferred</code> · <code>approved</code> · <code>rejected</code>.</p></div>
<div><h4>Confidence</h4></div>
<div><h4>Evidence ids</h4></div>
<div><h4>Receipt ids</h4></div>
<div><h4>Inferred-from references</h4></div>
<div><h4>Optional review fields</h4></div>
<div><h4>Creation timestamp</h4></div>

</div>

<div className="craik-keypoint">

**Review fields required for decided records.**

Approved and rejected preferences require reviewer, reason, and review
timestamp.

</div>

## Scope boundary

<div className="craik-fields">

<div>
<dt>Scope</dt>
<dt><span className="craik-fields__type">Subject prefix</span></dt>
<dd>Promotion rule</dd>
</div>

<div>
<dt>User preference</dt>
<dt><span className="craik-fields__type"><code>user:</code></span></dt>
<dd>Stays user-scoped.</dd>
</div>

<div>
<dt>Team preference</dt>
<dt><span className="craik-fields__type"><code>team:</code></span></dt>
<dd>Do not promote a user preference to team scope without an explicit review decision and evidence for the broader scope.</dd>
</div>

</div>

## What's next

<div className="craik-next">

<a href="../memory-review-nudges/">
<strong>Reference</strong>
<span>Memory review nudges</span>
<small>The reminder layer that surfaces stale preferences for review.</small>
</a>

<a href="../learning-receipts/">
<strong>Reference</strong>
<span>Learning receipts</span>
<small>The receipt subtype for preference reviews.</small>
</a>

<a href="../../guides/learning-loops/">
<strong>Guide</strong>
<span>Learning loops</span>
<small>The full discipline preference review sits inside.</small>
</a>

</div>
