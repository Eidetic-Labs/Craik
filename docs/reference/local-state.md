# Local State Layout

Craik uses one product-home directory by default:

```text
~/.craik/
```

`CRAIK_HOME` overrides the default.

The standard layout is:

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

Directory purposes:

| Directory | Purpose |
| --- | --- |
| `config/` | Local runtime configuration. |
| `secrets/` | Local credentials and tokens. |
| `state/` | SQLite databases and other durable runtime state. |
| `cache/` | Rebuildable local cache data. |
| `logs/` | Local operational logs. |
| `receipts/` | Capability receipts. |
| `handoffs/` | Durable agent handoffs. |
| `case-files/` | Task case files. |
| `projects/` | Project registry and project profiles. |

On POSIX systems, Craik creates these directories with owner-only permissions where supported.

The SQLite local store lives at `state/craik.sqlite3`. It is the persistence foundation for users who run Craik without Stigmem, but it remains single-node local state rather than shared Stigmem-backed truth.

Project-local `.craik/` directories are opt-in only. Resolving local state paths never creates project-local metadata inside a repository.
