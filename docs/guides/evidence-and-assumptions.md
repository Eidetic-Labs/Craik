# Evidence And Assumptions

<p className="craik-meta"><span>5 min read</span><span>For runners &amp; reviewers</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- The split Craik enforces between *evidence* (citable) and *assumptions*
  (unresolved claims).
- The shape of an evidence reference, and what the local assembler
  produces for every case file.
- The current assumption-ledger entries the runtime emits and what they
  mean.
- The honesty rules for promoting an assumption to a fact.

</div>

<div className="craik-keypoint">

**Two different objects, on purpose**

**Evidence** is source material the runtime can cite. **Assumptions** are
unresolved claims that should not be treated as facts yet. Conflating the
two is how an agent runtime starts hallucinating policy.

</div>

## Evidence references

Every piece of context the local case assembler loads becomes an
`evidence_reference` in the resulting case file. The local assembler
emits one for:

<div className="craik-grid">

<div>
<h4>The task request</h4>
<p>The original user request and the runtime's accepted interpretation.</p>
</div>

<div>
<h4>The project profile</h4>
<p>The registered project with its docs paths, immutable paths, and validation commands.</p>
</div>

<div>
<h4>Repository status</h4>
<p>Branch, head, clean/dirty, default branch, remote identity.</p>
</div>

<div>
<h4>Discovered documentation</h4>
<p>Mutable doc roots loaded into the case file as context.</p>
</div>

<div>
<h4>Discovered immutable documentation</h4>
<p>ADRs and other declared evidence paths — loaded as evidence, never as edit targets.</p>
</div>

</div>

Each evidence reference carries:

<div className="craik-fields">

<div>
<dt>Field</dt>
<dt><span className="craik-fields__type">Type</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt>source</dt>
<dt><span className="craik-fields__type">uri</span></dt>
<dd>Where this evidence came from — file path, GitHub URL, memory fact id.</dd>
</div>

<div>
<dt>kind</dt>
<dt><span className="craik-fields__type">enum</span></dt>
<dd><code>doc</code> · <code>immutable_doc</code> · <code>repo_state</code> · <code>memory_fact</code> · <code>handoff</code> · <code>github_issue</code> · <code>github_pr</code> · ...</dd>
</div>

<div>
<dt>locator</dt>
<dt><span className="craik-fields__type">string</span></dt>
<dd>A precise locator: file path with optional anchor, fact id, issue number.</dd>
</div>

<div>
<dt>summary</dt>
<dt><span className="craik-fields__type">text</span></dt>
<dd>A short, redaction-safe description.</dd>
</div>

<div>
<dt>metadata</dt>
<dt><span className="craik-fields__type">map</span></dt>
<dd>Free-form metadata. <code>immutable: true</code> for ADRs, <code>indexed_at</code> for staleness.</dd>
</div>

</div>

## The assumption ledger

When expected context is unavailable, the local assembler records an
**assumption** rather than fabricating evidence. Today's runtime emits
assumptions in these shapes:

<div className="craik-grid">

<div>
<h4>"Memory facts were not loaded"</h4>
<p>The project has no memory backend configured (or the backend was unreachable). Connect Stigmem or set <code>CRAIK_MEMORY_BACKEND</code>.</p>
</div>

<div>
<h4>"GitHub state was not loaded"</h4>
<p>The GitHub adapter was disabled, unconfigured, unauthenticated, or rate-limited. Issues and PRs are not part of this case file.</p>
</div>

<div>
<h4>"No mutable documentation files were discovered"</h4>
<p>The project has no docs paths declared, or every declared path was excluded by discovery. Likely a registration problem.</p>
</div>

<div>
<h4>"Some documentation was omitted by the context budget"</h4>
<p>Context budgeting trimmed candidate docs to keep the prompt deterministic. <code>context_budget.docs_excluded</code> names what got cut.</p>
</div>

</div>

The list grows as the runtime grows. The schema doesn't.

## The honesty rule

**Agents must not promote assumptions to memory or documentation claims
unless later evidence supports them.** This is the single most important
rule in the whole runtime — break it, and downstream case files start
inheriting unverifiable facts.

The promotion path is concrete:

<ol className="craik-steps">
<li>

**Find evidence.** Locate a file, issue, PR, or upstream fact that
supports the assumption.

</li>
<li>

**Attach the evidence reference.** When proposing memory or writing a
handoff, cite the new evidence directly.

</li>
<li>

**Note the promotion in the handoff.** Record that the assumption was
promoted, with the evidence id.

</li>
<li>

**Refute or carry forward when you can't.** If the evidence didn't
materialize, the assumption stays open. That's fine — that's what
"open assumption" means.

</li>
</ol>

## Immutable documentation as evidence

Immutable docs — ADRs especially — are first-class evidence. Case files
label them separately in `adrs` (or `immutable_docs`) and mark their
evidence reference with `metadata.immutable = true`:

```json title="An ADR evidence reference"
{
  "source": "docs/adr/0004-policy-envelope-shape.md",
  "kind": "immutable_doc",
  "locator": "docs/adr/0004-policy-envelope-shape.md",
  "summary": "Policy envelope shape ADR — defines runtime contract.",
  "metadata": {
    "immutable": true,
    "indexed_at": "2026-05-19T12:14:08Z"
  }
}
```

The `immutable` flag prevents downstream code from accidentally treating
the ADR as a mutable doc and proposing an edit.

## What's next

<div className="craik-next">

<a href="../../concepts/case-files/">
<strong>Read</strong>
<span>Case files</span>
<small>How evidence and assumptions compose into the per-task brief.</small>
</a>

<a href="../memory-proposals/">
<strong>Do</strong>
<span>Memory proposals</span>
<small>Promote an assumption to a fact via the proposal flow.</small>
</a>

<a href="../contradiction-inbox/">
<strong>Do</strong>
<span>Contradiction inbox</span>
<small>What to do when new evidence contradicts an existing fact.</small>
</a>

</div>
