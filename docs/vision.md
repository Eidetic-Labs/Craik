# Vision

<p className="craik-meta"><span>4 min read</span><span>For everyone</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**Why this doc matters**

Every other doc in this section is downstream of the vision. Read this
first to understand the thesis, the product category Craik is creating,
and the north star that decides what ships and what doesn't.

</div>

<div className="craik-keypoint">

**Craik exists to make agent work durable.**

Current agent tools are improving quickly, but most still treat useful
state as a side effect of a chat transcript, terminal log, or ad hoc
summary. That does not scale to teams, long-lived projects, or
multi-agent workflows.

</div>

Craik's central claim is that agents need an operating layer that gives
them:

<div className="craik-grid">

<div>
<h4>A shared model of the work</h4>
<p>Agents inherit the same case file, evidence, ADRs, traps, and
contradictions before they act.</p>
</div>

<div>
<h4>Evidence-backed memory</h4>
<p>Every durable assertion cites a source. Proposals flow through review;
nothing silently overwrites truth.</p>
</div>

<div>
<h4>Explicit authority boundaries</h4>
<p>Policy envelopes, capability grants, and immutable paths decide what an
agent may touch — not the agent's intuition.</p>
</div>

<div>
<h4>Structured handoffs</h4>
<p>Machine-readable continuity records the next actor can resume from. No
re-deriving state from chat logs.</p>
</div>

<div>
<h4>Durable artifacts</h4>
<p>Receipts, work-graph nodes, and exports survive the run — addressable
for audit and replay months later.</p>
</div>

<div>
<h4>A way to resolve disagreement</h4>
<p>Contradictions are first-class workflow items, not silent merge
conflicts.</p>
</div>

</div>

## Product category

Craik should not be positioned as another agent framework.

The intended category is:

> **Durable agent runtime.**

An agent framework helps developers wire agents to tools. A durable
agent runtime helps agents participate in long-running work with
continuity, accountability, and shared state.

## North star

<div className="craik-keypoint">

A new agent should be able to join a project and understand its current
state better than a human who has been away for two weeks.

</div>

That includes:

<div className="craik-grid">

<div>
<h4>Current goals</h4>
<p>The task queue, the active intent locks, and the accepted interpretations.</p>
</div>

<div>
<h4>Active branches</h4>
<p>Repo state, recent commits, default branch, dirty-vs-clean status.</p>
</div>

<div>
<h4>Relevant issues &amp; PRs</h4>
<p>Open issues, PRs in review, comments and check results — all loaded as evidence.</p>
</div>

<div>
<h4>Architecture constraints</h4>
<p>Immutable ADRs, design decisions, and the reasons behind them.</p>
</div>

<div>
<h4>Stale docs &amp; known risks</h4>
<p>Stale-risk markers, known traps, and negative knowledge from prior runs.</p>
</div>

<div>
<h4>Accepted conventions</h4>
<p>Validation commands, allowed autonomy, scope rules.</p>
</div>

<div>
<h4>Unresolved questions</h4>
<p>Open contradictions, missing context flagged in case files, exit-discipline
context requests.</p>
</div>

<div>
<h4>Facts other agents learned</h4>
<p>Stigmem-backed truth, with provenance and trust scope — not just chat
transcripts.</p>
</div>

</div>

## Design principles

The six principles every Craik feature is measured against.

<ol className="craik-steps">
<li>

**Memory is not a transcript.**
Durable memory should be structured, scoped, provenance-aware, and
reviewable.

</li>
<li>

**Agents should not silently rewrite reality.**
Contradictions become first-class workflow items, never silent merge
conflicts.

</li>
<li>

**Context should be assembled, not dumped.**
Agents receive task-specific case files that explain what matters and
why.

</li>
<li>

**Governance belongs in the runtime.**
Permissions, approvals, policy obligations, and receipts are part of
normal execution — not an enterprise add-on.

</li>
<li>

**Handoffs are artifacts.**
A final chat message is not enough. Agent work leaves structured state
for future agents.

</li>
<li>

**Local mode should exist, but not define the product.**
Craik should be easy to try without Stigmem, while making clear that
durable multi-agent work needs a real memory substrate.

</li>
</ol>

## Initial wedge

The first market wedge is **multi-agent software delivery for small
technical teams.** Concrete enough to prove the runtime — every piece
of the thesis is observable in software delivery:

<div className="craik-grid">

<div>
<h4>Repositories have history</h4>
<p>Git provides the durable substrate Craik's project model reads against.</p>
</div>

<div>
<h4>ADRs and docs go stale</h4>
<p>Stale-risk and contradictions are inherent — not edge cases.</p>
</div>

<div>
<h4>CI and PRs create verifiable artifacts</h4>
<p>Verification commands, check results, and review state are first-class.</p>
</div>

<div>
<h4>Issues encode work</h4>
<p>Task surfaces already exist, so Craik's task contract has real grounding.</p>
</div>

<div>
<h4>Agents need context</h4>
<p>Software work is context-heavy. Case files demonstrate value immediately.</p>
</div>

<div>
<h4>Handoffs matter</h4>
<p>Teams already feel the pain of "what did the last person mean"; structured
handoffs land naturally.</p>
</div>

</div>

If Craik works here, it can expand into incident response, research
operations, compliance workflows, support engineering, and other
long-running knowledge work.

## What's next

<div className="craik-next">

<a href="product-strategy.md">
<strong>Read next</strong>
<span>Product strategy</span>
<small>How the vision becomes positioning — agent runner strategy, license, gateway ergonomics.</small>
</a>

<a href="differentiators.md">
<strong>Read</strong>
<span>Differentiators</span>
<small>What keeps the roadmap from collapsing into basic CLI plumbing.</small>
</a>

<a href="concepts/project-model.md">
<strong>Concept</strong>
<span>Project model</span>
<small>The foundational typed object the rest of the runtime composes against.</small>
</a>

</div>
