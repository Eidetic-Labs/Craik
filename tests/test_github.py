import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import pytest

from craik.runtime.case_files import CaseFileAssembler
from craik.runtime.github import (
    GitHubAuthError,
    GitHubClient,
    GitHubConfig,
    GitHubRateLimitError,
    GitHubReadAdapter,
    parse_github_remote,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.project_registry import ProjectRegistry
from craik.runtime.store import LocalStore
from craik.runtime.tasks import create_task


@pytest.fixture
def store(tmp_path: Path):
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_parse_github_remote_supports_common_remote_shapes() -> None:
    assert parse_github_remote("https://github.com/Eidetic-Labs/Craik.git").full_name == (
        "Eidetic-Labs/Craik"
    )
    assert parse_github_remote("git@github.com:Eidetic-Labs/Craik.git").full_name == (
        "Eidetic-Labs/Craik"
    )
    assert parse_github_remote("ssh://git@github.com/Eidetic-Labs/Craik.git").full_name == (
        "Eidetic-Labs/Craik"
    )
    assert parse_github_remote("https://example.com/Eidetic-Labs/Craik.git") is None


def test_github_read_adapter_loads_repo_issues_pr_files_and_status() -> None:
    with _github_api() as api:
        adapter = GitHubReadAdapter(
            GitHubClient(GitHubConfig(api_url=api.url, token="test-token"))
        )

        state = adapter.case_file_state(
            remote="https://github.com/Eidetic-Labs/Craik.git",
            ref="abc123",
        )

    assert state["status"] == "loaded"
    assert state["authenticated"] is True
    assert state["metadata"]["full_name"] == "Eidetic-Labs/Craik"
    assert state["issues"][0]["number"] == 16
    assert state["pull_requests"][0]["changed_files"] == ["src/craik/runtime/github.py"]
    assert state["check_status"] == {"state": "success", "total_count": 2}


def test_github_adapter_handles_missing_auth() -> None:
    with _github_api(require_auth=True) as api:
        client = GitHubClient(GitHubConfig(api_url=api.url))

        with pytest.raises(GitHubAuthError, match="authentication failed"):
            client.repository(parse_github_remote("https://github.com/Eidetic-Labs/Craik.git"))


def test_github_adapter_maps_rate_limit_errors() -> None:
    with _github_api(rate_limited=True) as api:
        client = GitHubClient(GitHubConfig(api_url=api.url, token="test-token"))

        with pytest.raises(GitHubRateLimitError, match="rate limit exceeded"):
            client.repository(parse_github_remote("https://github.com/Eidetic-Labs/Craik.git"))


def test_case_file_includes_loaded_github_state(
    tmp_path: Path,
    store: LocalStore,
) -> None:
    repo = _repo(tmp_path)
    _run_git(repo, "remote", "add", "origin", "https://github.com/Eidetic-Labs/Craik.git")
    project = ProjectRegistry(store).add_project(repo, name="Example")
    task = create_task(
        store,
        title="Review GitHub context",
        objective="Build case with GitHub context.",
        project_id=project.id,
        mode="review",
    )

    with _github_api() as api:
        adapter = GitHubReadAdapter(
            GitHubClient(GitHubConfig(api_url=api.url, token="test-token"))
        )
        case_file = CaseFileAssembler(store, github_adapter=adapter).build(task.id)

    assert case_file.github_state["status"] == "loaded"
    assert case_file.github_state["repo"] == "Eidetic-Labs/Craik"
    statements = {assumption.statement for assumption in case_file.assumptions}
    assert "No GitHub issue or pull request state was loaded into this case file." not in statements


def test_case_file_records_github_fallback_assumption(
    tmp_path: Path,
    store: LocalStore,
) -> None:
    repo = _repo(tmp_path)
    project = ProjectRegistry(store).add_project(repo, name="Example")
    task = create_task(
        store,
        title="Review local context",
        objective="Build case without GitHub remote.",
        project_id=project.id,
    )

    with _github_api() as api:
        adapter = GitHubReadAdapter(
            GitHubClient(GitHubConfig(api_url=api.url, token="test-token"))
        )
        case_file = CaseFileAssembler(store, github_adapter=adapter).build(task.id)

    assert case_file.github_state["status"] == "not_configured"
    assert any("No GitHub issue" in item.statement for item in case_file.assumptions)


class _Node:
    def __init__(self, server: HTTPServer, thread: threading.Thread) -> None:
        self._server = server
        self._thread = thread
        self.url = f"http://127.0.0.1:{server.server_port}"

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)


class _github_api:
    def __init__(self, *, require_auth: bool = False, rate_limited: bool = False) -> None:
        self._require_auth = require_auth
        self._rate_limited = rate_limited
        self._node: _Node | None = None

    def __enter__(self) -> _Node:
        require_auth = self._require_auth
        rate_limited = self._rate_limited

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if rate_limited:
                    self._json({"message": "rate limit"}, status=403, rate_limited=True)
                    return
                if require_auth and self.headers.get("Authorization") != "Bearer test-token":
                    self._json({"message": "bad credentials"}, status=401)
                    return
                path = self.path.split("?", 1)[0]
                if path == "/repos/Eidetic-Labs/Craik":
                    self._json(
                        {
                            "full_name": "Eidetic-Labs/Craik",
                            "default_branch": "main",
                            "private": True,
                            "open_issues_count": 3,
                        }
                    )
                    return
                if path == "/repos/Eidetic-Labs/Craik/issues":
                    self._json(
                        [
                            {
                                "number": 16,
                                "title": "Implement GitHub read adapter",
                                "state": "open",
                                "html_url": "https://github.com/Eidetic-Labs/Craik/issues/16",
                                "updated_at": "2026-05-15T22:11:50Z",
                            },
                            {
                                "number": 37,
                                "title": "Merged PR",
                                "state": "open",
                                "pull_request": {},
                            },
                        ]
                    )
                    return
                if path == "/repos/Eidetic-Labs/Craik/pulls":
                    self._json(
                        [
                            {
                                "number": 37,
                                "title": "feat: add memory diff previews",
                                "state": "open",
                                "html_url": "https://github.com/Eidetic-Labs/Craik/pull/37",
                                "head": {"ref": "issue-15-memory-diff-preview"},
                                "base": {"ref": "main"},
                            }
                        ]
                    )
                    return
                if path == "/repos/Eidetic-Labs/Craik/pulls/37/files":
                    self._json([{"filename": "src/craik/runtime/github.py"}])
                    return
                if path.startswith("/repos/Eidetic-Labs/Craik/commits/") and path.endswith(
                    "/status"
                ):
                    self._json({"state": "success", "total_count": 2})
                    return
                self._json({"message": "not found"}, status=404)

            def log_message(self, format: str, *args: Any) -> None:
                return

            def _json(
                self,
                payload: dict[str, Any] | list[dict[str, Any]],
                *,
                status: int = 200,
                rate_limited: bool = False,
            ) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                if rate_limited:
                    self.send_header("X-RateLimit-Remaining", "0")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self._node = _Node(server, thread)
        return self._node

    def __exit__(self, *args: object) -> None:
        if self._node is not None:
            self._node.close()


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Example\n")
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "config", "user.email", "test@example.com")
    _run_git(repo, "config", "user.name", "Test User")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-m", "initial")
    return repo


def _run_git(cwd: Path, *args: str) -> None:
    result = subprocess_run(cwd, *args)
    assert result.returncode == 0, result.stderr


def subprocess_run(cwd: Path, *args: str):
    import subprocess

    return subprocess.run(
        ("git", "-C", str(cwd), *args),
        check=False,
        text=True,
        capture_output=True,
    )
