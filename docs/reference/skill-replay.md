# Skill replay

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The three records that compose skill replay — fixture, observation,
result — and the boundary that keeps replays reproducible without
raw payloads.

</div>

<div className="craik-keypoint">

**Failures block promotion.**

Failed replay results block skill promotion until reviewed.

</div>

## Records

<div className="craik-fields">

<div>
<dt>Record</dt>
<dt><span className="craik-fields__type">Captures</span></dt>
<dd>Fields</dd>
</div>

<div>
<dt><code>SkillReplayFixture</code></dt>
<dt><span className="craik-fields__type">fixture</span></dt>
<dd>Fixture id · skill package id · fixture name · input references · expected outcome · expected output references · evidence ids · redaction status · redacted metadata.</dd>
</div>

<div>
<dt><code>SkillReplayObservation</code></dt>
<dt><span className="craik-fields__type">observed</span></dt>
<dd>Current behavior for a fixture — outcome · output references · validation signal ids · telemetry id · receipt ids · redacted metadata.</dd>
</div>

<div>
<dt><code>SkillReplayResult</code></dt>
<dt><span className="craik-fields__type">result</span></dt>
<dd>From <code>replay_skill_fixture</code> — pass/fail status · reason · expected and observed outcome · missing output refs · unexpected output refs · telemetry id · receipt ids · timestamp.</dd>
</div>

</div>

## Fixture expectations

<div className="craik-keypoint">

**Redacted and evidence-backed.**

Replay fixtures reference case files, worker results, telemetry,
receipts, and evidence by id — never raw prompts, outputs, traces,
stdout, stderr, payloads, responses, or credentials.

</div>

## What's next

<div className="craik-next">

<a href="skill-promotion-gates/">
<strong>Reference</strong>
<span>Skill promotion gates</span>
<small>The promotion decision replay results gate.</small>
</a>

<a href="skill-proposals/">
<strong>Reference</strong>
<span>Skill proposals</span>
<small>The proposal that requires fixture ids for high-risk plans.</small>
</a>

<a href="memory-review-nudges/">
<strong>Reference</strong>
<span>Memory review nudges</span>
<small>The companion review-only signal.</small>
</a>

</div>
