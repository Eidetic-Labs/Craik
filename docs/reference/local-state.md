# Local state layout

<p className="craik-meta"><span>2 min read</span><span>Reference</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll find here**

The Craik product-home layout under `~/.craik/` (or
`$CRAIK_HOME`) — what each subdirectory holds, the permissions
posture, and the project-local opt-in rule.

</div>

<div className="craik-keypoint">

**One product home, opt-in project metadata.**

Project-local <code>.craik/</code> directories are opt-in only.
Resolving local-state paths never creates project-local metadata
inside a repository.

</div>

## Default home

```text
~/.craik/
```

`CRAIK_HOME` overrides the default.

## Layout

```text
~/.craik/
  config/
  secrets/
  state/
  cache/
  logs/
  receipts/
  handoffs/
  case-files/
  projects/
```

<div className="craik-fields">

<div>
<dt>Directory</dt>
<dt><span className="craik-fields__type">Holds</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt><code>config/</code></dt>
<dt><span className="craik-fields__type">runtime</span></dt>
<dd>Local runtime configuration.</dd>
</div>

<div>
<dt><code>secrets/</code></dt>
<dt><span className="craik-fields__type">credentials</span></dt>
<dd>Local credentials and tokens. Owner-only on POSIX.</dd>
</div>

<div>
<dt><code>state/</code></dt>
<dt><span className="craik-fields__type">durable</span></dt>
<dd>SQLite databases and other durable runtime state.</dd>
</div>

<div>
<dt><code>cache/</code></dt>
<dt><span className="craik-fields__type">disposable</span></dt>
<dd>Rebuildable local cache data.</dd>
</div>

<div>
<dt><code>logs/</code></dt>
<dt><span className="craik-fields__type">operational</span></dt>
<dd>Local operational logs.</dd>
</div>

<div>
<dt><code>receipts/</code></dt>
<dt><span className="craik-fields__type">audit</span></dt>
<dd>Capability receipts.</dd>
</div>

<div>
<dt><code>handoffs/</code></dt>
<dt><span className="craik-fields__type">durable</span></dt>
<dd>Agent handoffs.</dd>
</div>

<div>
<dt><code>case-files/</code></dt>
<dt><span className="craik-fields__type">task</span></dt>
<dd>Task case files.</dd>
</div>

<div>
<dt><code>projects/</code></dt>
<dt><span className="craik-fields__type">registry</span></dt>
<dd>Project registry and project profiles.</dd>
</div>

</div>

<div className="craik-keypoint">

**SQLite is single-node local state.**

The local store lives at <code>state/craik.sqlite3</code>. It is the
persistence foundation for users who run Craik without Stigmem, but
it remains single-node local state rather than shared
Stigmem-backed truth.

</div>

## What's next

<div className="craik-next">

<a href="local-store/">
<strong>Reference</strong>
<span>Local store</span>
<small>The SQLite contract catalog inside <code>state/</code>.</small>
</a>

<a href="../guides/configuring-craik-home/">
<strong>Guide</strong>
<span>Configuring Craik home</span>
<small>Relocation rules and CI conventions.</small>
</a>

<a href="config/">
<strong>Reference</strong>
<span>Config reference</span>
<small>The env-var surface that drives this layout.</small>
</a>

</div>
