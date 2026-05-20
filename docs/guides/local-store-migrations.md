# Local store migrations

<p className="craik-meta"><span>3 min read</span><span>For operators &amp; maintainers</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll do**

Understand how Craik's local-state migrations run, where versions are
tracked, how compatibility fixtures keep older stores on a path
forward, and what to do when a migration fails.

</div>

<div className="craik-keypoint">

**Forward-only, never silent.**

Migrations run during <code>LocalStore.initialize()</code>. Craik
never silently recreates an unreadable local store — receipts,
handoffs, memory proposals, case files, and task runs may be needed
for audit or recovery.

</div>

## Version tracking

<div className="craik-fields">

<div>
<dt>Where</dt>
<dt><span className="craik-fields__type">Records</span></dt>
<dd>Notes</dd>
</div>

<div>
<dt>SQLite <code>PRAGMA user_version</code></dt>
<dt><span className="craik-fields__type">current</span></dt>
<dd>The current migration number.</dd>
</div>

<div>
<dt><code>migrations</code> table</dt>
<dt><span className="craik-fields__type">history</span></dt>
<dd>One row per applied migration.</dd>
</div>

<div>
<dt><code>local_store_metadata</code></dt>
<dt><span className="craik-fields__type">metadata</span></dt>
<dd>Created by migration 2 · updated by later framework migrations · records current store schema version and the contract registry count visible to the installed Craik build.</dd>
</div>

</div>

## Migration runner

Craik applies local-store migrations through a registered,
forward-only runner. Each migration has an integer version, a stable
name, and one function that mutates SQLite state. The registry must be
contiguous from version 1 to the current supported migration; gaps fail
at import time rather than leaving operators with an ambiguous upgrade
path.

The v0.2 migration framework keeps the existing v1 and v2 behavior and
adds migration 3 as an example metadata migration. Migration 3 records
that the store was upgraded through the registered migration framework.

## Compatibility fixtures

Migration compatibility tests load prior schema fixtures from
`tests/fixtures/local_store/`. The v1 fixture describes the first
records-based store layout and is migrated to the current schema
during tests. This keeps old local stores on an explicit compatibility
path instead of depending only on fresh database initialization.

## Failure handling

If a migration fails, Craik raises a local-store migration error with
recovery guidance.

<ol className="craik-steps">
<li>Back up <code>state/craik.sqlite3</code>.</li>
<li>Keep the original file unchanged.</li>
<li>Run <code>craik doctor</code> for diagnostics.</li>
<li>If the database version is newer than the installed Craik build supports, upgrade Craik before opening the store.</li>
<li>If a migration failed partway through, restore the backup or copy the database aside before retrying.</li>
</ol>

## What's next

<div className="craik-next">

<a href="../doctor/">
<strong>Guide</strong>
<span>Doctor diagnostics</span>
<small>The first command to run when a migration fails.</small>
</a>

<a href="../../reference/local-store/">
<strong>Reference</strong>
<span>Local store</span>
<small>The persistence-layer reference.</small>
</a>

<a href="../updating/">
<strong>Guide</strong>
<span>Updating Craik</span>
<small>When to expect a migration during an upgrade.</small>
</a>

</div>
