# Mobile companion app decision

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `MobileCompanionSurface` contract — required controls, decision
rules, blocked behaviors, and the current shipped posture.

</div>

<div className="craik-keypoint">

**Not a credential cache.**

A mobile companion may expose review notifications and explicit
operator-triggered actions — it must not become a credential cache or
uncontrolled remote automation channel.

</div>

## What it records

<div className="craik-grid">

<div><h4>Surface id</h4></div>
<div><h4>Support level</h4><p><code>supported</code> · <code>experimental</code> · <code>deferred</code>.</p></div>
<div><h4>Operator consent requirement</h4></div>
<div><h4>Policy context preservation</h4></div>
<div><h4>Evidence link preservation</h4></div>
<div><h4>Receipt requirement</h4></div>
<div><h4>Credential storage posture</h4></div>
<div><h4>Encrypted device storage posture</h4></div>
<div><h4>Push notification controls</h4></div>
<div><h4>Remote action controls</h4></div>
<div><h4>Offline action controls</h4></div>
<div><h4>Documentation reference</h4></div>

</div>

## Decision rules

<div className="craik-decision">

<div>
<h4>Allowed (supported)</h4>
<ul>
<li>Explicit operator consent</li>
<li>Encrypted device storage</li>
<li>Push notification controls</li>
<li>Remote action controls</li>
<li>Offline action controls</li>
<li>Policy context</li>
<li>Evidence links</li>
<li>Receipts</li>
</ul>
</div>

<div>
<h4>Blocked</h4>
<ul>
<li>Stores credentials</li>
<li>Skips operator consent</li>
<li>Unencrypted device storage</li>
<li>Omits push notification controls</li>
<li>Uncontrolled remote or offline actions</li>
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

Reviewable notifications and explicit operator-triggered actions can
be supported. Always-on automation, credential storage, uncontrolled
remote actions, and offline action queues without receipts are
deferred.

</div>

## What's next

<div className="craik-next">

<a href="../desktop-companion/">
<strong>Reference</strong>
<span>Desktop companion</span>
<small>The desktop counterpart.</small>
</a>

<a href="../accessibility-requirements/">
<strong>Reference</strong>
<span>Accessibility requirements</span>
<small>The accessibility floor every companion respects.</small>
</a>

<a href="../../guides/companion-app-security/">
<strong>Guide</strong>
<span>Companion app security</span>
<small>The author-facing security posture.</small>
</a>

</div>
