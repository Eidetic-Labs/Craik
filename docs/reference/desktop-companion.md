# Desktop companion app decision

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `DesktopCompanionSurface` contract — required controls, decision
rules, blocked behaviors, and the current shipped posture.

</div>

<div className="craik-keypoint">

**Governed surface, not background automation.**

A desktop companion may present status, notifications, and controlled
actions — it must not become an unreviewed background automation
channel.

</div>

## What it records

<div className="craik-grid">

<div><h4>Surface id</h4></div>
<div><h4>Support level</h4><p><code>supported</code> · <code>experimental</code> · <code>deferred</code>.</p></div>
<div><h4>Operator consent requirement</h4></div>
<div><h4>Policy context preservation</h4></div>
<div><h4>Evidence link preservation</h4></div>
<div><h4>Receipt requirement</h4></div>
<div><h4>Local storage encryption posture</h4></div>
<div><h4>Secret storage posture</h4></div>
<div><h4>Notification controls</h4></div>
<div><h4>Background action controls</h4></div>
<div><h4>Documentation reference</h4></div>

</div>

## Decision rules

<div className="craik-decision">

<div>
<h4>Allowed (supported)</h4>
<ul>
<li>Explicit operator consent</li>
<li>Encrypted local storage</li>
<li>Notification controls</li>
<li>Background action controls</li>
<li>Policy context</li>
<li>Evidence links</li>
<li>Receipts</li>
</ul>
</div>

<div>
<h4>Blocked</h4>
<ul>
<li>Stores secrets</li>
<li>Skips operator consent</li>
<li>Unencrypted local storage</li>
<li>Omits notification controls</li>
<li>Uncontrolled background actions</li>
<li>Loses policy or evidence links</li>
<li>Skips receipts</li>
</ul>
</div>

</div>

Experimental surfaces require explicit review. Deferred surfaces are
not available as product surfaces.

## Current posture

<div className="craik-keypoint">

**Governed extension point.**

Status panels, reviewable notifications, and explicit operator-triggered
actions can be supported when they satisfy the controls above.
Always-on automation, secret caching, uncontrolled background actions,
and private local-state synchronization are deferred until a later
roadmap gate adds stronger product and security requirements.

</div>

## What's next

<div className="craik-next">

<a href="mobile-companion/">
<strong>Reference</strong>
<span>Mobile companion</span>
<small>The mobile counterpart.</small>
</a>

<a href="accessibility-requirements/">
<strong>Reference</strong>
<span>Accessibility requirements</span>
<small>The accessibility floor every companion respects.</small>
</a>

<a href="../guides/companion-app-security/">
<strong>Guide</strong>
<span>Companion app security</span>
<small>The author-facing security posture.</small>
</a>

</div>
