# Project Profile

Project profiles describe repositories Craik can reason about.

Schema:

```text
craik.project_profile
```

Important fields:

| Field | Purpose |
| --- | --- |
| `id` | Stable project id derived from the project name. |
| `name` | Human-readable project name. |
| `repo.local_path` | Absolute path to the Git repository root. |
| `repo.remote` | `origin` remote URL when configured. |
| `repo.default_branch` | Detected default branch. |
| `docs.paths` | Documentation paths Craik should inspect. |
| `docs.immutable_paths` | Paths that should not be edited by normal workflows. |
| `memory.backend` | Default memory backend for the project. |
| `memory.scope` | Default memory scope for the project. |

## Git Detection

`craik project add` accepts any path inside a Git repository and stores the repository root.

Default branch detection prefers `origin/HEAD`, then the current branch, then `main`.

## Default Paths

When documentation paths are not provided, Craik detects conventional paths that exist:

- `README.md`
- `docs/`

When immutable paths are not provided, Craik detects conventional ADR paths that exist:

- `docs/adr/`
- `docs/adrs/`

## Immutable Paths

Immutable paths are policy inputs for later write protection. Register them explicitly when a project uses a non-standard decision-record path:

```sh
craik project add /path/to/repo --immutable-path architecture/decisions/
```

