# Configuring Craik Home

<p className="craik-meta"><span>4 min read</span><span>For operators</span><span>Updated 2026-05-19</span></p>

<div className="craik-lead">

**What you'll learn**

- Where Craik writes state by default and how to move it.
- The directory layout `craik home init` creates.
- How to share a home between hosts or CI runners.
- How to inspect a home without modifying it.

</div>

## The default location

Craik stores everything it persists — projects, tasks, case files,
receipts, handoffs, secrets, and caches — under one product-home directory:

```text
~/.craik/
```

This is intentional. One known location keeps backups, audit, and cleanup
trivial. Craik does **not** silently create project-local `.craik/`
directories inside your repositories. Project-local metadata is opt-in
and explicitly documented when used.

## Override with `CRAIK_HOME`

Point Craik at any directory you control by setting `CRAIK_HOME`:

```bash title="Move Craik home to a tmpfs sandbox"
export CRAIK_HOME=/tmp/craik-sandbox
craik home init
```

`CRAIK_HOME` must:

- Be an absolute path.
- Point at a directory Craik can read and write.
- Be available before *any* `craik` command runs — Craik reads the
  variable at process start.

Setting `CRAIK_HOME` per-command works too:

```bash title="One-off home override"
CRAIK_HOME=/tmp/scratch craik home show
```

## The home layout

```text
$CRAIK_HOME/
  config/       # user-level config and credential profile definitions
  secrets/      # secret material — never committed
  state/        # SQLite store: projects, tasks, receipts, handoffs, case files
  cache/        # short-lived caches
  logs/         # diagnostic logs
  receipts/     # exported receipts
  handoffs/     # exported handoffs
  case-files/   # exported case files
  projects/     # per-project artifacts and exports
```

Each directory has a single, narrow purpose. Separation by data class keeps
backup policies straightforward (back up `state/` and `secrets/`; you can
typically rebuild `cache/`) and makes audit easier (everything actor-relevant
ends up in `receipts/` and `handoffs/`).

## Inspect vs initialize

<div className="craik-cmd">
<code>craik home show</code>
<p>Print the resolved paths. <strong>Read-only.</strong> Does not create directories.</p>
</div>

<div className="craik-cmd">
<code>craik home init</code>
<p>Create the per-data-class subdirectories. Idempotent — safe to re-run.</p>
</div>

Run `craik home show` first in any unfamiliar shell to confirm where Craik
is pointing before you trigger work.

## Sharing a home across hosts

A few real situations:

<div className="craik-grid">

<div>
<h4>One workstation, many shells</h4>
<p>Use the default <code>~/.craik/</code>. Every shell sees the same home unless someone exports <code>CRAIK_HOME</code>.</p>
</div>

<div>
<h4>CI runner</h4>
<p>Set <code>CRAIK_HOME</code> early in the job (e.g., <code>$GITHUB_WORKSPACE/.craik</code>). Cache it between jobs if you want project registrations to persist; otherwise treat each job as a fresh home.</p>
</div>

<div>
<h4>Team-shared host</h4>
<p>Give each operator their own <code>CRAIK_HOME</code> under <code>/srv/craik/&lt;user&gt;</code>. Don't share <code>state/</code> across operators — receipts and handoffs are bound to operator identity.</p>
</div>

<div>
<h4>Containerized run</h4>
<p>Mount <code>CRAIK_HOME</code> as a volume so receipts and handoffs survive the container. Treat <code>secrets/</code> as a separate secret-tier volume.</p>
</div>

</div>

:::caution
**Don't put `CRAIK_HOME` on a network share unless you know what you're
doing.** The SQLite store at `state/craik.sqlite` is sensitive to file
locking semantics. NFS will work most of the time and surprise you at the
worst possible moment. Stick to local disks or volumes that promise
POSIX locking.
:::

## Resetting a home

Because Craik never writes outside `CRAIK_HOME`, resetting state is one
command:

```bash title="Tear down a Craik home"
rm -rf "$CRAIK_HOME"
craik home init
```

This wipes projects, tasks, case files, receipts, handoffs, secrets, and
caches. Use it only when you really mean it.

## What's next

<div className="craik-next">

<a href="setup.md">
<strong>Do</strong>
<span>Run the setup wizard</span>
<small>An interactive walkthrough that wires home, identity, and a first project together.</small>
</a>

<a href="doctor.md">
<strong>Diagnose</strong>
<span>Run doctor</span>
<small>Health-check Craik home, identity, credentials, and provider posture.</small>
</a>

<a href="../reference/local-state.md">
<strong>Reference</strong>
<span>Local state layout</span>
<small>The on-disk shape of every directory under <code>CRAIK_HOME</code>.</small>
</a>

</div>
