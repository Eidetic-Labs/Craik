"""Run the documented quickstart demo path from a clean local state."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def main() -> int:
    craik = shutil.which("craik")
    if craik is None:
        print("craik console script is not available on PATH", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="craik-quickstart-smoke-") as raw_tmp:
        tmp = Path(raw_tmp)
        repo = tmp / "stigmem"
        home = tmp / "home"
        _seed_repo(repo)
        payload = _run_demo(craik=craik, repo=repo, home=home)
        _assert_payload(payload)
    return 0


def _seed_repo(repo: Path) -> None:
    (repo / "docs" / "adr").mkdir(parents=True)
    (repo / "README.md").write_text("# Stigmem\n", encoding="utf-8")
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (repo / "docs" / "adr" / "0001-record.md").write_text("# ADR\n", encoding="utf-8")
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "add", "README.md", "docs")
    _run_git(repo, "commit", "-m", "initial")


def _run_demo(*, craik: str, repo: Path, home: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            craik,
            "demo",
            "stigmem-docs",
            "--repo-path",
            str(repo),
            "--no-github",
        ],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "CRAIK_HOME": str(home)},
    )
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise AssertionError("quickstart demo did not return a JSON object")
    return payload


def _assert_payload(payload: dict[str, Any]) -> None:
    assert payload["schema"] == "craik.demo.stigmem_docs_reconciliation"
    assert payload["status"] == "runnable"
    assert payload["case_file_id"] == "case_stigmem_documentation_reconciliation"
    assert payload["receipt_ids"] == ["receipt_demo_stigmem_documentation_reconciliation"]
    assert payload["handoff_id"] == "handoff_stigmem_documentation_reconciliation"
    assert payload["memory_write"]["status"] == "proposal_created"
    assert payload["work_graph_id"] == "graph_task_stigmem_documentation_reconciliation"
    assert [item["provider_id"] for item in payload["provider_executions"]] == [
        "provider_openai",
        "provider_anthropic",
    ]
    assert {item["run_status"] for item in payload["provider_executions"]} == {"completed"}
    assert "craik case show task_stigmem_documentation_reconciliation" in payload[
        "next_commands"
    ]
    assert "craik handoff show task_stigmem_documentation_reconciliation" in payload[
        "next_commands"
    ]
    assert "craik graph export --task-id task_stigmem_documentation_reconciliation" in payload[
        "next_commands"
    ]
    assert any(
        command.startswith("craik contradictions show ")
        for command in payload["next_commands"]
    )
    assert any(command.startswith("craik memory show ") for command in payload["next_commands"])


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ("git", *args),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_AUTHOR_NAME": "Craik Quickstart Smoke",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Craik Quickstart Smoke",
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
