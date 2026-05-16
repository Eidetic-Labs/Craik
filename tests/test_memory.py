import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import pytest

from craik.contracts.models import CapabilityGrant, CapabilityTarget
from craik.runtime.memory import (
    DirectMemoryWriteDeniedError,
    EphemeralMemoryStore,
    EvidenceRequiredError,
    LocalMemoryStore,
    StigmemAuthError,
    StigmemClient,
    StigmemConfig,
    StigmemMemoryStore,
    StigmemPermissionError,
    build_memory_diff,
    create_proposal,
    evidence_reference,
    fact_reference,
    memory_write_failure,
    preview_memory_impact,
)
from craik.runtime.paths import ensure_craik_home
from craik.runtime.policy import generate_policy_envelope
from craik.runtime.store import LocalStore


@pytest.fixture
def store(tmp_path: Path):
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    local_store = LocalStore.from_paths(paths)
    local_store.initialize()
    try:
        yield local_store
    finally:
        local_store.close()


def test_ephemeral_backend_proposal_lifecycle() -> None:
    backend = EphemeralMemoryStore()
    proposal = _proposal()

    backend.propose(proposal)
    approved = backend.approve(proposal.id, decided_by="user:reviewer", reason="Supported.")

    assert approved.status == "approved"
    assert approved.decided_by == "user:reviewer"
    assert backend.search("local proposals") == [approved.fact]


def test_local_backend_persists_proposals(store: LocalStore) -> None:
    backend = LocalMemoryStore(store)
    proposal = _proposal()

    backend.propose(proposal)

    assert backend.get_proposal(proposal.id) == proposal
    assert backend.list_proposals(task_id="task_docs", status="pending") == [proposal]


def test_approval_requires_evidence(store: LocalStore) -> None:
    proposal = create_proposal(
        task_id="task_docs",
        entity="repo:example",
        relation="craik:status",
        value="No evidence attached.",
        source="agent:codex",
        confidence=0.5,
        scope="local",
        trust_class="reported",
        evidence=[],
    )
    backend = LocalMemoryStore(store)
    backend.propose(proposal)

    with pytest.raises(EvidenceRequiredError, match="requires evidence"):
        backend.approve(proposal.id, decided_by="user:reviewer", reason="Unsupported.")


def test_reject_records_decision(store: LocalStore) -> None:
    backend = LocalMemoryStore(store)
    proposal = _proposal()
    backend.propose(proposal)

    rejected = backend.reject(proposal.id, decided_by="user:reviewer", reason="Too broad.")

    assert rejected.status == "rejected"
    assert rejected.decision_reason == "Too broad."
    assert backend.search("local proposals") == []


def test_direct_local_memory_write_requires_policy_grant(store: LocalStore) -> None:
    proposal = _proposal()

    with pytest.raises(DirectMemoryWriteDeniedError, match="memory.write grant"):
        LocalMemoryStore(store).write_fact(proposal.fact)


def test_stigmem_backend_detects_capabilities_and_queries_local_node() -> None:
    with _stigmem_node() as node:
        backend = StigmemMemoryStore(
            StigmemClient(StigmemConfig(node_url=node.url, api_key="test-key"))
        )

        capabilities = backend.discover()
        facts = backend.search("local proposals")
        fact = backend.get_fact("fact_1")
        provenance = backend.get_provenance("fact_1")

    assert capabilities.backend == "stigmem"
    assert capabilities.node_id == "stigmem:node:test"
    assert capabilities.auth_required is True
    assert capabilities.required.fact_query is True
    assert capabilities.optional.recall is False
    assert facts[0].value == "Local proposals require review."
    assert fact.entity == "repo:example"
    assert provenance["sources"] == ["README.md"]


def test_stigmem_backend_maps_auth_failures() -> None:
    with _stigmem_node() as node:
        backend = StigmemMemoryStore(
            StigmemClient(StigmemConfig(node_url=node.url, api_key="wrong-key"))
        )

        with pytest.raises(StigmemAuthError, match="authentication failed"):
            backend.search("local proposals")


def test_stigmem_backend_maps_permission_failures() -> None:
    with _stigmem_node(deny_write=True) as node:
        backend = StigmemMemoryStore(
            StigmemClient(StigmemConfig(node_url=node.url, api_key="test-key"))
        )
        proposal = _proposal()
        policy = generate_policy_envelope(task_id="task_docs", actor="agent:codex")

        with pytest.raises(StigmemPermissionError, match="permission denied"):
            backend.write_fact(
                proposal.fact,
                policy=policy,
                grants=[_memory_write_grant()],
            )


def test_stigmem_direct_write_requires_policy_grant() -> None:
    with _stigmem_node() as node:
        backend = StigmemMemoryStore(
            StigmemClient(StigmemConfig(node_url=node.url, api_key="test-key"))
        )
        proposal = _proposal()
        policy = generate_policy_envelope(task_id="task_docs", actor="agent:codex")

        with pytest.raises(DirectMemoryWriteDeniedError, match="matching capability grant"):
            backend.write_fact(proposal.fact, policy=policy, grants=[])

        written = backend.write_fact(
            proposal.fact,
            policy=policy,
            grants=[_memory_write_grant()],
        )

    assert written.value == "Local proposals require review before promotion."


def test_memory_diff_tracks_proposal_decisions_and_fact_activity() -> None:
    created = _proposal()
    approved = created.model_copy(update={"id": "memprop_approved", "status": "approved"})
    rejected = created.model_copy(update={"id": "memprop_rejected", "status": "rejected"})
    other_task = created.model_copy(update={"id": "memprop_other", "task_id": "task_other"})
    written = fact_reference(approved.fact, fact_id="fact_approved", cid="sha256:approved")
    failure = memory_write_failure(fact=rejected.fact, reason="permission denied")

    diff = build_memory_diff(
        task_id="task_docs",
        proposals=[created, approved, rejected, other_task],
        facts_written=[written],
        write_failures=[failure],
        facts_read=[fact_reference(created.fact, fact_id="fact_read")],
    )

    assert diff.proposals_created == [
        "memprop_approved",
        "memprop_docs_repo_example_craik_memory",
        "memprop_rejected",
    ]
    assert diff.proposals_approved == ["memprop_approved"]
    assert diff.proposals_rejected == ["memprop_rejected"]
    assert diff.facts_written == [written]
    assert diff.write_failures[0].reason == "permission denied"
    assert diff.facts_read[0].id == "fact_read"


def test_memory_impact_preview_shows_scope_evidence_and_contradictions() -> None:
    existing = _proposal().fact.model_copy(update={"value": "Older value."})
    add = _proposal()
    invalidate = create_proposal(
        task_id="task_docs",
        entity="repo:example",
        relation="craik:obsolete",
        value="Outdated fact.",
        source="docs/old.md",
        confidence=0.6,
        scope="company",
        trust_class="reported",
        operation="invalidate",
        evidence=[],
    )

    preview = preview_memory_impact(
        task_id="task_docs",
        proposals=[add, invalidate],
        existing_facts=[existing],
    )

    assert [fact.relation for fact in preview.facts_to_add] == ["craik:memory"]
    assert [fact.relation for fact in preview.facts_to_invalidate] == ["craik:obsolete"]
    assert preview.evidence_missing == [invalidate.id]
    assert preview.scope_summary == {"company": 1, "local": 1}
    assert preview.likely_contradictions[0].existing_value == "Older value."
    assert "different value" in preview.likely_contradictions[0].reason


def test_memory_diff_and_preview_redact_secret_like_values() -> None:
    proposal = create_proposal(
        task_id="task_docs",
        entity="repo:example",
        relation="craik:secret",
        value="token=redactionfixture123",
        source="Authorization: Bearer redactionfixture123",
        confidence=0.5,
        scope="local",
        trust_class="reported",
        evidence=[],
    )

    preview = preview_memory_impact(
        task_id="task_docs",
        proposals=[proposal],
        existing_facts=[],
    )
    failure = memory_write_failure(fact=proposal.fact, reason="api_key=redactionfixture123")

    assert "redactionfixture" not in preview.model_dump_json()
    assert "redactionfixture" not in failure.model_dump_json()


def _proposal():
    evidence = evidence_reference(
        task_id="task_docs",
        source="README.md",
        locator="README.md#memory",
        summary="README documents local proposals.",
    )
    return create_proposal(
        task_id="task_docs",
        entity="repo:example",
        relation="craik:memory",
        value="Local proposals require review before promotion.",
        source="README.md",
        confidence=0.9,
        scope="local",
        trust_class="observed",
        evidence=[evidence],
    )


def _memory_write_grant() -> CapabilityGrant:
    return CapabilityGrant(
        id="grant_memory_write",
        task_id="task_docs",
        capability="memory.write",
        target=CapabilityTarget(),
        operations=["write"],
        reason="Test memory write grant.",
        approved_by="user:maintainer",
    )


class _Node:
    def __init__(self, server: HTTPServer, thread: threading.Thread) -> None:
        self._server = server
        self._thread = thread
        self.url = f"http://127.0.0.1:{server.server_port}"

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)


class _stigmem_node:
    def __init__(self, *, deny_write: bool = False) -> None:
        self._deny_write = deny_write
        self._node: _Node | None = None

    def __enter__(self) -> _Node:
        deny_write = self._deny_write

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path == "/healthz":
                    self._json({"status": "ok"})
                    return
                if self.path == "/.well-known/stigmem":
                    self._json(
                        {
                            "node_id": "stigmem:node:test",
                            "node_url": self.server_url(),
                            "auth": {"required": True},
                            "federation": False,
                            "source_attestation": "off",
                        }
                    )
                    return
                if self.path.startswith("/v1/facts"):
                    if not self._authorized():
                        self._json({"error": "unauthorized"}, status=401)
                        return
                    if self.path.startswith("/v1/facts/fact_1/provenance"):
                        self._json({"fact_id": "fact_1", "sources": ["README.md"]})
                        return
                    if self.path.startswith("/v1/facts/fact_1"):
                        self._json(_fact_payload())
                        return
                    self._json({"facts": [_fact_payload()]})
                    return
                self._json({"error": "not found"}, status=404)

            def do_POST(self) -> None:
                if self.path == "/v1/facts":
                    if not self._authorized():
                        self._json({"error": "unauthorized"}, status=401)
                        return
                    if deny_write:
                        self._json({"error": "forbidden"}, status=403)
                        return
                    content_length = int(self.headers.get("Content-Length", "0"))
                    payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                    self._json(payload, status=201)
                    return
                self._json({"error": "not found"}, status=404)

            def log_message(self, format: str, *args: Any) -> None:
                return

            def server_url(self) -> str:
                return f"http://127.0.0.1:{self.server.server_port}"

            def _authorized(self) -> bool:
                return self.headers.get("Authorization") == "Bearer test-key"

            def _json(self, payload: dict[str, Any], *, status: int = 200) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
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


def _fact_payload() -> dict[str, Any]:
    return {
        "id": "fact_1",
        "entity": "repo:example",
        "relation": "craik:memory",
        "value": {"type": "text", "v": "Local proposals require review."},
        "source": "README.md",
        "confidence": 0.9,
        "scope": "team",
        "trust_class": "observed",
    }
