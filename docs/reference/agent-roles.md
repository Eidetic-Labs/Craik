# Agent roles

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The `craik.agent_role` contract that bounds v0.3.0 multi-agent
coordination. Roles describe responsibility and authority — they do
not grant new runtime permissions by themselves.

</div>

<div className="craik-keypoint">

**Roles describe; policy decides.**

Role authority is explicit. Policy envelopes and capability grants
still control side effects.

</div>

## Supported role kinds

| Kind | Responsibility |
| --- | --- |
| `orchestrator` | Coordinate specialists, preserve outputs, decide routing. |
| `implementer` | Produce scoped implementation work. |
| `verifier` | Validate behavior, tests, and acceptance criteria. |
| `adversarial_reviewer` | Look for failure modes, regressions, weak assumptions. |
| `policy_reviewer` | Check policy, grants, receipts, redaction boundaries. |
| `docs_reviewer` | Review documentation, operator instructions, examples. |
| `memory_curator` | Review memory proposals, stale risks, contradiction boundaries. |
| `adjudicator` | Decide between reviewed outputs or defer unresolved disagreements. |

## Authority values

Role authority is one of: `coordinate` · `read` · `propose` · `review`
· `adjudicate` · `implement`.

## Record contents

Each role records:

<div className="craik-grid">

<div><h4>Expected input schemas</h4></div>
<div><h4>Expected output schemas</h4></div>
<div><h4>Handoff &amp; receipt obligations</h4></div>
<div><h4>Redaction requirements</h4></div>
<div><h4>Optional runner identity</h4></div>

</div>

## What's next

<div className="craik-next">

<a href="cross-agent-review/">
<strong>Reference</strong>
<span>Cross-agent review</span>
<small>How specialist roles request and produce reviews.</small>
</a>

<a href="debates/">
<strong>Reference</strong>
<span>Structured debates</span>
<small>How roles produce typed disagreement records.</small>
</a>

<a href="../adr/credential-and-identity-architecture/">
<strong>ADR</strong>
<span>0007 · Credential &amp; identity</span>
<small>Why operator/credential identity isolates per role.</small>
</a>

</div>
