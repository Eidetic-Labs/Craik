# Runtime critics and red team

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The two typed review-input contracts —
`craik.runtime_critic_finding` and `craik.red_team_finding`. Both are
reviewable signals, not authoritative decisions.

</div>

<div className="craik-keypoint">

**Reviewable signals until adjudicated.**

Both contracts set `authoritative` to `false`. They become settled
only after an adjudication record accepts, rejects, revises, or defers
them.

</div>

## Runtime critic findings

`craik.runtime_critic_finding` captures quality issues found before
accepting a major output, handoff, or memory write.

<div className="craik-grid">

<div><h4>Unsupported claims</h4></div>
<div><h4>Policy violations</h4></div>
<div><h4>Scope drift</h4></div>
<div><h4>Missing validation</h4></div>
<div><h4>Stale evidence</h4></div>
<div><h4>Missing handoffs</h4></div>
<div><h4>Unredacted sensitive content</h4></div>
<div><h4>Risky memory writes</h4></div>

</div>

**Preserved fields:** severity · rationale · affected artifacts ·
evidence ids · proposed actions · review status · optional
adjudication link.

<div className="craik-keypoint">

**Required evidence.**

High and critical critic findings must include proposed actions.
Findings about unsupported claims or stale evidence must include
evidence ids.

</div>

## Red-team findings

`craik.red_team_finding` captures adversarial review results for
high-risk work.

<div className="craik-grid">

<div><h4>Prompt injection</h4></div>
<div><h4>Privilege escalation</h4></div>
<div><h4>Data exfiltration</h4></div>
<div><h4>Destructive action</h4></div>
<div><h4>Policy bypass</h4></div>
<div><h4>Memory poisoning</h4></div>
<div><h4>Adversarial input</h4></div>
<div><h4>Other attack paths</h4></div>

</div>

A blocker must be high or critical severity and must include proposed
actions.

## Authority boundary

<div className="craik-keypoint">

**Surface, don't settle.**

Callers surface reviewable blockers before durable handoffs or memory
promotion — but they do not treat finding text as settled fact without
adjudication.

</div>

## What's next

<div className="craik-next">

<a href="../quality-scores/">
<strong>Reference</strong>
<span>Quality scores</span>
<small>The companion review records.</small>
</a>

<a href="../cross-agent-review/">
<strong>Reference</strong>
<span>Cross-agent review</span>
<small>The adjudication flow these findings feed.</small>
</a>

<a href="../quality-gate-view/">
<strong>Reference</strong>
<span>Quality gate view</span>
<small>The operator surface for findings and scores.</small>
</a>

</div>
