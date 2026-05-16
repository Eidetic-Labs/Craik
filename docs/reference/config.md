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
