# GitHub config

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The environment variables that configure Craik's read-only v0.1.0
GitHub adapter — and the token-handling boundary.

</div>

<div className="craik-keypoint">

**Read-only in v0.1.0.**

Tokens are only sent in the <code>Authorization</code> header. Craik
redacts token-shaped values from stored state and does not print
configured tokens.

</div>

## Variables

<div className="craik-fields">

<div>
<dt>Variable</dt>
<dt><span className="craik-fields__type">Default</span></dt>
<dd>Purpose</dd>
</div>

<div>
<dt><code>CRAIK_GITHUB_TOKEN</code></dt>
<dt><span className="craik-fields__type">unset</span></dt>
<dd>Preferred bearer token for GitHub API reads.</dd>
</div>

<div>
<dt><code>GITHUB_TOKEN</code></dt>
<dt><span className="craik-fields__type">unset</span></dt>
<dd>Fallback bearer token.</dd>
</div>

<div>
<dt><code>CRAIK_GITHUB_API_URL</code></dt>
<dt><span className="craik-fields__type"><code>https://api.github.com</code></span></dt>
<dd>API base URL.</dd>
</div>

<div>
<dt><code>CRAIK_GITHUB_TIMEOUT</code></dt>
<dt><span className="craik-fields__type"><code>5.0</code></span></dt>
<dd>Request timeout in seconds.</dd>
</div>

</div>

<div className="craik-keypoint">

**Unauthenticated reads have caveats.**

Unauthenticated reads may work for public repositories but are subject
to lower rate limits and cannot access private repository data.

</div>

## What's next

<div className="craik-next">

<a href="../guides/github-adapter/">
<strong>Guide</strong>
<span>GitHub adapter</span>
<small>How the adapter loads context.</small>
</a>

<a href="config/">
<strong>Reference</strong>
<span>Config reference</span>
<small>The wider config surface.</small>
</a>

<a href="redaction/">
<strong>Reference</strong>
<span>Redaction</span>
<small>How token-shaped values stay out of state.</small>
</a>

</div>
