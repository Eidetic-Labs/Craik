# Memory And Stigmem

<p className="craik-meta"><span>6 min read</span><span>Core concept</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- Why Craik treats memory as governed project state, not a transcript cache.
- The proposal-first contract for agent-created memory updates.
- The split of responsibility between Craik and Stigmem.
- What Craik v0.1.0 actually does with memory today.

</div>

<div className="craik-keypoint">

**Proposal-first**

Agent-created memory updates default to **proposals** — durable, evidence-
backed candidate facts that remain reviewable until a human (or a policy
grant) promotes them. Direct durable writes are a separate, explicit
capability.

</div>

## Why "proposal-first"?

Memory that gets written silently corrupts the runtime. Once a fact lands
without evidence or review, every downstream case file that loads it
inherits an unverifiable claim — and the contradiction surfaces weeks
later as a mysterious disagreement nobody can attribute.

The proposal-first contract makes the failure mode loud instead. Every
agent-initiated update is a `craik.memory_proposal` record with:

<div className="craik-grid">

<div>
<h4>Evidence</h4>
<p>References back to the source — repo file, GitHub issue, prior handoff, upstream fact, run receipt.</p>
</div>

<div>
<h4>Scope</h4>
<p>The memory scope the proposal targets. Narrow scopes are easier to approve and easier to retire.</p>
</div>

<div>
<h4>Reason</h4>
<p>Why this proposal exists. The reviewer's first question.</p>
</div>

<div>
<h4>Visibility</h4>
<p>Approved local proposals become searchable local facts. Rejected and pending proposals remain visible for audit.</p>
</div>

</div>

## Direct writes are a separate capability

Direct durable memory writes require an explicit `memory.write` policy
authority. This applies to local and Stigmem-backed workflows alike.

When a runner attempts a memory write **without** that authority, Craik:

<ol className="craik-steps">
<li>Refuses the write.</li>
<li>Creates a memory proposal with the would-be fact and an evidence reference to the attempt.</li>
<li>Records a receipt naming the missing capability so the operator can decide whether to grant it.</li>
</ol>

This pattern is intentional. **Memory writes ride the same approval flow
as any other privileged capability.** No special path lets a runner widen
its authority by virtue of "the agent said so."

## Craik vs Stigmem: who owns what

<div className="craik-decision">

<div>
<h4>Craik owns</h4>
<ul>
<li>Orchestration: tasks, case files, handoffs, runners.</li>
<li>Receipts and the work graph.</li>
<li>Policy, capability grants, redaction, immutable paths.</li>
<li>Operator workflows: review, approval, contradiction handling.</li>
<li>Local memory state in degraded / offline mode.</li>
</ul>
</div>

<div>
<h4>Stigmem owns</h4>
<ul>
<li>Durable facts and provenance.</li>
<li>Memory scopes and trust metadata.</li>
<li>Contradiction tracking across scopes.</li>
<li>Federation between Stigmem nodes.</li>
<li>Auth and plugin hooks for the memory substrate itself.</li>
</ul>
</div>

</div>

Craik can run in **degraded local mode** without Stigmem — proposals,
diffs, previews, and read paths all work against the local SQLite store.
For real team-scale memory, Stigmem is the reference substrate.

## What v0.1.0 actually does

The current MVP behaviour is precise and conservative:

<ul>
<li><strong>Detects minimum Stigmem compatibility</strong> through a versioned API negotiation.</li>
<li><strong>Reads facts</strong> through the Stigmem HTTP API.</li>
<li><strong>Gets fact provenance</strong> so case files can cite where memory came from.</li>
<li><strong>Keeps local memory proposals</strong> regardless of whether Stigmem is reachable.</li>
<li><strong>Builds memory diffs and impact previews</strong> for every task that touched memory.</li>
<li><strong>Denies direct writes without grants</strong> — proposals are the fallback.</li>
<li><strong>Creates demo memory proposals</strong> through <code>craik demo stigmem-docs</code> so the contract is exercised end-to-end in CI.</li>
</ul>

Case files currently mark missing memory facts as **assumptions**. As the
case-file assembler grows a Stigmem fact loader, those assumptions get
replaced by actual evidence references — the schema doesn't change, just
the completeness.

## The memory lifecycle in one diagram

```text
agent run ──proposal──▶ memory_proposal (pending)
                              │
                              ├── reviewer approves ──▶ fact (local)
                              ├── reviewer rejects  ──▶ stays as audit
                              └── promotion expires ──▶ stays pending
```

Memory diffs (`craik memory diff <task>`) and impact previews
(`craik memory preview <task>`) are the operator surfaces that drive this
lifecycle.

## A pragmatic checklist

When you're deciding what to do with a pending proposal:

<ol className="craik-steps">
<li>

**Read the evidence.** Every proposal cites at least one evidence
reference. If the reference doesn't actually support the claim, reject.

</li>
<li>

**Check the scope.** A proposal that wants to land in a wide scope
(`org:*`) deserves more skepticism than one scoped to a single project.

</li>
<li>

**Look at contradictions.** The impact preview surfaces collisions
with existing approved facts. Resolve before approving.

</li>
<li>

**Promote, reject, or carry forward.** All three are legitimate
outcomes — the wrong move is to leave proposals stale and untriaged.

</li>
</ol>

## What's next

<div className="craik-next">

<a href="../../guides/memory-proposals/">
<strong>Do</strong>
<span>Manage memory proposals</span>
<small>The proposal lifecycle from creation to approval to retirement.</small>
</a>

<a href="../../guides/contradiction-inbox/">
<strong>Do</strong>
<span>Resolve contradictions</span>
<small>How conflicting facts surface and how the inbox tracks resolutions.</small>
</a>

<a href="../../reference/memory-backends/">
<strong>Reference</strong>
<span>Memory backends</span>
<small>Configuration for local memory and Stigmem-backed memory.</small>
</a>

</div>
