# Config Reference

Craik v0.1.0 is configured primarily through environment variables and local
state under `CRAIK_HOME`.

## Local State

| Variable | Purpose |
| --- | --- |
| `CRAIK_HOME` | Overrides the default `~/.craik` state directory. |

Craik stores runtime state in a SQLite database under `CRAIK_HOME/state/`.
Project-local `.craik/` directories are opt-in only and are not created by the
current CLI.

## Setup

`craik setup` creates the local home layout, initializes the local store, and
writes a default `craik.gateway_config` record. The command prints
`secrets_written = false` and does not collect API keys, channel tokens, webhook
secrets, or bearer credentials.

## Context Discovery

Project profiles can store documentation discovery overrides through
`craik project add`:

| Option | Purpose |
| --- | --- |
| `--discovery-exclude <glob>` | Adds a project-level context exclusion rule. |
| `--discovery-include <glob>` | Adds a project-level include rule that can restore a default-excluded path. |

`craik case build` accepts the same options as one-off user overrides for a
single case-file build. Craik always starts from conservative defaults that skip
generated, dependency, build, cache, and archive-heavy paths. The resulting case
file records active rules and skipped paths in `context_budget`.

## Stigmem

| Variable | Purpose |
| --- | --- |
| `CRAIK_STIGMEM_URL` | Base URL for the Stigmem node. |
| `CRAIK_STIGMEM_API_KEY` | Bearer token for authenticated Stigmem nodes. |
| `CRAIK_STIGMEM_TIMEOUT` | Request timeout in seconds. Defaults to `5.0`. |

Do not commit API keys to repository files. Craik redacts token-shaped values
from persisted payloads and command output.

## GitHub

| Variable | Purpose |
| --- | --- |
| `CRAIK_GITHUB_TOKEN` | Preferred bearer token for GitHub API reads. |
| `GITHUB_TOKEN` | Fallback bearer token. |
| `CRAIK_GITHUB_API_URL` | GitHub API base URL. Defaults to `https://api.github.com`. |
| `CRAIK_GITHUB_TIMEOUT` | Request timeout in seconds. Defaults to `5.0`. |

The GitHub adapter is read-only in v0.1.0.

## Validation

Use these commands before publishing changes:

```sh
uv run --python 3.12 --extra dev ruff check .
uv run --python 3.12 --extra dev mypy
uv run --python 3.12 --extra dev pytest
uv run --python 3.12 --extra dev craik policy test
```
