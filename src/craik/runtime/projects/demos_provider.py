"""Provider-backed demo entrypoints."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from craik.runtime.github import GitHubReadAdapter
from craik.runtime.projects.demos import StigmemDocsDemo
from craik.runtime.store import LocalStore


@dataclass(frozen=True)
class ProviderBackedStigmemDocsDemo:
    """Run the Stigmem docs demo through one selected provider."""

    store: LocalStore
    github_adapter: GitHubReadAdapter | None = None

    def run(
        self,
        *,
        repo_path: Path,
        provider_id: str,
        live_enabled: bool,
        project_name: str = "Stigmem",
        stigmem_url: str | None = None,
        stigmem_api_key: str | None = None,
        github: bool = True,
        max_tokens: int = 24000,
    ) -> dict[str, Any]:
        """Run reconciliation and surface provider output for demos."""
        result = StigmemDocsDemo(
            self.store,
            github_adapter=self.github_adapter,
        ).run(
            repo_path=repo_path,
            project_name=project_name,
            stigmem_url=stigmem_url,
            stigmem_api_key=stigmem_api_key,
            github=github,
            provider_ids=(provider_id,),
            live_provider_enabled=live_enabled,
            max_tokens=max_tokens,
        )
        provider_execution = result["provider_executions"][0]
        provider_results = provider_execution.get("provider_results", [])
        result["provider_demo"] = {
            "mode": "live" if live_enabled else "fixture",
            "provider_id": provider_id,
            "run_id": provider_execution.get("run_id"),
            "receipt_ids": provider_execution.get("receipt_ids", []),
            "findings": provider_execution.get("model_findings", []),
            "results": provider_results,
        }
        return result
