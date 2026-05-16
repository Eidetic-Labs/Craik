# GitHub Config

Craik's GitHub adapter is read-only in v0.1.0.

Configuration:

| Variable | Purpose |
| --- | --- |
| `CRAIK_GITHUB_TOKEN` | Preferred bearer token for GitHub API reads. |
| `GITHUB_TOKEN` | Fallback bearer token. |
| `CRAIK_GITHUB_API_URL` | GitHub API base URL. Defaults to `https://api.github.com`. |
| `CRAIK_GITHUB_TIMEOUT` | Request timeout in seconds. Defaults to `5.0`. |

Tokens are only sent in the `Authorization` header. Craik redacts token-shaped values from stored state and does not print configured tokens.

Unauthenticated reads may work for public repositories but are subject to lower rate limits and cannot access private repository data.
