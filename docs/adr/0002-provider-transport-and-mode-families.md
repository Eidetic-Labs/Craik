# ADR 0002 · Provider transport and mode families

<p className="craik-meta"><span>2 min read</span><span>Accepted</span><span>Recorded 2026-05-01</span></p>

<div className="craik-lead">

**What this ADR decides**

That Craik separates provider families from transport. Provider
adapters own payload shape, streaming, errors, and result
normalization. Transports own delivery and chunk parsing. OpenAI
Responses, Anthropic Messages, and OpenAI-compatible Chat Completions
are three distinct provider families.

</div>

<div className="craik-keypoint">

**Status: Accepted.**

A single generic HTTP provider would hide tool, streaming, usage, and
retry differences. Splitting transport from family keeps each axis
testable and lets fixture transports cover provider tests offline.

</div>

## Context

Craik needs one provider path that can run fixtures, local
OpenAI-compatible servers, and hosted OpenAI and Anthropic APIs. The
OpenAI Responses API, Anthropic Messages API, and Chat
Completions–compatible servers are related but not interchangeable wire
formats. Treating them as one adapter would hide tool, streaming,
usage, and retry differences.

## Decision

<div className="craik-decision">

<div>
<h4>Provider adapters</h4>
<p>Own payload construction · streaming normalization · error classification · result normalization.</p>
</div>

<div>
<h4>Transports</h4>
<p>Own delivery and chunk parsing. <code>FixtureTransport</code> keeps tests offline; <code>HTTPTransport</code> uses stdlib urllib for live JSON and SSE.</p>
</div>

</div>

**Three distinct provider families:**

<div className="craik-grid">

<div><h4>OpenAI Responses</h4></div>
<div><h4>Anthropic Messages</h4></div>
<div><h4>Chat Completions (OAI-compatible)</h4><p>Covers Ollama · vLLM · LM Studio · OpenRouter-shaped endpoints.</p></div>

</div>

## Consequences

Provider tests can exercise adapters without network access. Live
transport hardening can evolve without rewriting provider-specific
schemas. The cost is a small amount of family-specific normalization
code and certification coverage for each supported family.

## Alternatives considered

<div className="craik-fields">

<div>
<dt>Alternative</dt>
<dt><span className="craik-fields__type">Disposition</span></dt>
<dd>Why rejected</dd>
</div>

<div>
<dt>Single generic HTTP provider</dt>
<dt><span className="craik-fields__type">rejected</span></dt>
<dd>Would push schema branches into callers and receipts.</dd>
</div>

<div>
<dt>SDK dependencies</dt>
<dt><span className="craik-fields__type">rejected for MVP</span></dt>
<dd>Stdlib HTTP keeps package release and CI behavior simpler.</dd>
</div>

</div>

<div className="craik-keypoint">

**Retraction: none active.**

Retract this ADR if Craik moves provider execution into an external
provider gateway with its own typed transport contract.

</div>

## What's next

<div className="craik-next">

<a href="../../reference/model-providers/">
<strong>Reference</strong>
<span>Model providers</span>
<small>The shipped provider matrix this ADR shapes.</small>
</a>

<a href="../record-mvp-runner-scope/">
<strong>ADR</strong>
<span>0001 · Record MVP runner scope</span>
<small>Why the runner path is fixture-backed by default.</small>
</a>

<a href="../../guides/provider-routing/">
<strong>Guide</strong>
<span>Provider routing</span>
<small>How to configure each provider family.</small>
</a>

</div>
