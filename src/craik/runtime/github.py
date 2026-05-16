"""Read-only GitHub adapter for case file context."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request

from craik.runtime.redaction import redact


class GitHubError(RuntimeError):
    """Base error for GitHub adapter failures."""


class GitHubRateLimitError(GitHubError):
    """Raised when GitHub rate limits the adapter."""


class GitHubAuthError(GitHubError):
    """Raised when GitHub rejects authentication."""


class GitHubRequestError(GitHubError):
    """Raised when a GitHub request fails."""


@dataclass(frozen=True)
class GitHubConfig:
    """Read-only GitHub API settings."""

    api_url: str = "https://api.github.com"
    token: str | None = None
    timeout_seconds: float = 5.0

    @classmethod
    def from_env(cls, env: dict[str, str]) -> GitHubConfig:
        """Load GitHub settings from environment values."""
        return cls(
            api_url=env.get("CRAIK_GITHUB_API_URL", "https://api.github.com"),
            token=env.get("CRAIK_GITHUB_TOKEN") or env.get("GITHUB_TOKEN"),
            timeout_seconds=float(env.get("CRAIK_GITHUB_TIMEOUT", "5.0")),
        )


@dataclass(frozen=True)
class GitHubRepository:
    """Parsed GitHub repository identity."""

    owner: str
    name: str

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


class GitHubClient:
    """Small dependency-free read-only GitHub API client."""

    def __init__(self, config: GitHubConfig) -> None:
        self._config = config
        self._api_url = config.api_url.rstrip("/")

    @property
    def authenticated(self) -> bool:
        return bool(self._config.token)

    def repository(self, repo: GitHubRepository) -> dict[str, Any]:
        payload = self._get(f"/repos/{repo.owner}/{repo.name}")
        if not isinstance(payload, dict):
            raise GitHubRequestError("GitHub repository response must be an object")
        return payload

    def issues(self, repo: GitHubRepository, *, limit: int = 10) -> list[dict[str, Any]]:
        payload = self._get(
            f"/repos/{repo.owner}/{repo.name}/issues",
            params={"state": "open", "per_page": str(limit)},
        )
        return [
            item
            for item in _list_payload(payload, "GitHub issues response must be a list")
            if "pull_request" not in item
        ]

    def pull_requests(self, repo: GitHubRepository, *, limit: int = 10) -> list[dict[str, Any]]:
        payload = self._get(
            f"/repos/{repo.owner}/{repo.name}/pulls",
            params={"state": "open", "per_page": str(limit)},
        )
        return _list_payload(payload, "GitHub pull requests response must be a list")

    def changed_files(
        self,
        repo: GitHubRepository,
        pull_number: int,
        *,
        limit: int = 50,
    ) -> list[str]:
        payload = self._get(
            f"/repos/{repo.owner}/{repo.name}/pulls/{pull_number}/files",
            params={"per_page": str(limit)},
        )
        return [
            str(item["filename"])
            for item in _list_payload(payload, "GitHub pull request files response must be a list")
            if "filename" in item
        ]

    def check_status(self, repo: GitHubRepository, ref: str) -> dict[str, Any]:
        payload = self._get(f"/repos/{repo.owner}/{repo.name}/commits/{ref}/status")
        if not isinstance(payload, dict):
            raise GitHubRequestError("GitHub commit status response must be an object")
        return {
            "state": _redacted_str(payload.get("state", "unknown")),
            "total_count": int(payload.get("total_count", 0)),
        }

    def _get(self, path: str, *, params: dict[str, str] | None = None) -> Any:
        url = f"{self._api_url}{path}"
        if params:
            url = f"{url}?{parse.urlencode(params)}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "craik-read-adapter",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._config.token:
            headers["Authorization"] = f"Bearer {self._config.token}"
        http_request = request.Request(url, headers=headers, method="GET")
        try:
            with request.urlopen(http_request, timeout=self._config.timeout_seconds) as response:
                data = response.read()
        except error.HTTPError as exc:
            _raise_github_http_error(exc)
        except error.URLError as exc:
            raise GitHubRequestError(f"GitHub request failed: {exc.reason}") from exc
        if not data:
            return {}
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise GitHubRequestError("GitHub response was not valid JSON") from exc


class GitHubReadAdapter:
    """Build read-only GitHub state for case files."""

    def __init__(self, client: GitHubClient) -> None:
        self._client = client

    def case_file_state(self, *, remote: str | None, ref: str, limit: int = 10) -> dict[str, Any]:
        """Return redacted GitHub state for a project remote."""
        repo = parse_github_remote(remote)
        if repo is None:
            return {
                "status": "not_configured",
                "authenticated": self._client.authenticated,
                "warnings": ["Project remote is not a GitHub repository."],
            }

        state: dict[str, Any] = {
            "status": "loaded",
            "authenticated": self._client.authenticated,
            "repo": repo.full_name,
            "warnings": [],
        }
        try:
            metadata = self._client.repository(repo)
            issues = self._client.issues(repo, limit=limit)
            pull_requests = self._client.pull_requests(repo, limit=limit)
            state["metadata"] = _repo_metadata(metadata)
            state["issues"] = [_issue_summary(issue) for issue in issues]
            state["pull_requests"] = [
                _pull_request_summary(
                    pull_request,
                    changed_files=self._changed_files(repo, pull_request),
                )
                for pull_request in pull_requests
            ]
            state["check_status"] = self._client.check_status(repo, ref)
        except GitHubError as exc:
            state["status"] = (
                "partial" if any(key in state for key in ("metadata", "issues")) else "error"
            )
            state["warnings"].append(str(redact(str(exc)).value))
        return state

    def _changed_files(self, repo: GitHubRepository, pull_request: dict[str, Any]) -> list[str]:
        number = pull_request.get("number")
        if not isinstance(number, int):
            return []
        try:
            return self._client.changed_files(repo, number)
        except GitHubError:
            return []


def parse_github_remote(remote: str | None) -> GitHubRepository | None:
    """Parse HTTPS or SSH GitHub remotes."""
    if not remote:
        return None
    patterns = (
        r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?/?$",
        r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"^ssh://git@github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.match(pattern, remote)
        if match:
            return GitHubRepository(
                owner=str(redact(match.group("owner")).value),
                name=str(redact(match.group("repo")).value),
            )
    return None


def _repo_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "full_name": _redacted_str(payload.get("full_name", "")),
        "default_branch": _redacted_str(payload.get("default_branch", "")),
        "private": bool(payload.get("private", False)),
        "open_issues_count": int(payload.get("open_issues_count", 0)),
    }


def _issue_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "number": int(payload.get("number", 0)),
        "title": _redacted_str(payload.get("title", "")),
        "state": _redacted_str(payload.get("state", "unknown")),
        "html_url": _redacted_str(payload.get("html_url", "")),
        "updated_at": _redacted_str(payload.get("updated_at", "")),
    }


def _pull_request_summary(payload: dict[str, Any], *, changed_files: list[str]) -> dict[str, Any]:
    return {
        "number": int(payload.get("number", 0)),
        "title": _redacted_str(payload.get("title", "")),
        "state": _redacted_str(payload.get("state", "unknown")),
        "html_url": _redacted_str(payload.get("html_url", "")),
        "head_ref": _redacted_str(_nested(payload, "head", "ref")),
        "base_ref": _redacted_str(_nested(payload, "base", "ref")),
        "changed_files": [_redacted_str(path) for path in changed_files],
    }


def _nested(payload: dict[str, Any], key: str, nested_key: str) -> Any:
    value = payload.get(key)
    if isinstance(value, dict):
        return value.get(nested_key, "")
    return ""


def _redacted_str(value: Any) -> str:
    return str(redact(str(value)).value)


def _list_payload(payload: Any, message: str) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise GitHubRequestError(message)
    return [item for item in payload if isinstance(item, dict)]


def _raise_github_http_error(exc: error.HTTPError) -> None:
    if exc.code == 401:
        raise GitHubAuthError("GitHub authentication failed") from exc
    if exc.code == 403:
        remaining = exc.headers.get("X-RateLimit-Remaining")
        if remaining == "0":
            raise GitHubRateLimitError("GitHub rate limit exceeded") from exc
        raise GitHubRequestError("GitHub permission denied") from exc
    raise GitHubRequestError(f"GitHub request failed with HTTP {exc.code}") from exc
