"""Memory backend interfaces and local proposal flow."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, Protocol, cast
from urllib import error, parse, request

from craik.contracts.models import (
    CapabilityGrant,
    FactValue,
    MemoryBackendCapabilities,
    MemoryContradictionPreview,
    MemoryDiff,
    MemoryFactReference,
    MemoryImpactPreview,
    MemoryOptionalCapabilities,
    MemoryProposal,
    MemoryRequiredCapabilities,
    MemoryScope,
    MemoryWriteFailure,
    PolicyEnvelope,
    TrustClass,
)
from craik.runtime.memory import memory_errors as _memory_errors
from craik.runtime.memory import memory_proposals as _memory_proposals
from craik.runtime.memory.memory_errors import (
    DirectMemoryWriteDeniedError as DirectMemoryWriteDeniedError,
)
from craik.runtime.memory.memory_errors import (
    MemoryProposalNotFoundError as MemoryProposalNotFoundError,
)
from craik.runtime.memory.memory_errors import (
    StigmemAuthError as StigmemAuthError,
)
from craik.runtime.memory.memory_errors import (
    StigmemCapabilityError as StigmemCapabilityError,
)
from craik.runtime.memory.memory_errors import (
    StigmemPermissionError as StigmemPermissionError,
)
from craik.runtime.memory.memory_errors import (
    StigmemRequestError as StigmemRequestError,
)
from craik.runtime.policy.policy import check_memory_grant
from craik.runtime.policy.redaction import redact
from craik.runtime.store import LocalStore

LiteralSourceAttestation = Literal["warn", "enforce", "off"]


class MemoryStore(Protocol):
    """Common memory backend behavior used by Craik."""

    def propose(self, proposal: MemoryProposal) -> MemoryProposal:
        """Store a reviewable memory proposal."""

    def get_proposal(self, proposal_id: str) -> MemoryProposal | None:
        """Load one proposal."""

    def list_proposals(
        self,
        *,
        task_id: str | None = None,
        status: str | None = None,
    ) -> list[MemoryProposal]:
        """List proposals with optional filters."""

    def approve(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        """Approve a proposal for local memory use."""

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        """Reject a proposal."""

    def search(self, query: str) -> list[FactValue]:
        """Search approved local facts."""


class EphemeralMemoryStore:
    """In-memory backend for tests and demos."""

    def __init__(self) -> None:
        self._proposals: dict[str, MemoryProposal] = {}

    def propose(self, proposal: MemoryProposal) -> MemoryProposal:
        self._proposals[proposal.id] = proposal
        return proposal

    def get_proposal(self, proposal_id: str) -> MemoryProposal | None:
        return self._proposals.get(proposal_id)

    def list_proposals(
        self,
        *,
        task_id: str | None = None,
        status: str | None = None,
    ) -> list[MemoryProposal]:
        proposals = sorted(self._proposals.values(), key=lambda proposal: proposal.id)
        return _filter_proposals(proposals, task_id=task_id, status=status)

    def approve(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = _require_proposal(self.get_proposal(proposal_id), proposal_id)
        approved = _memory_proposals.approve_proposal(
            proposal, decided_by=decided_by, reason=reason
        )
        self._proposals[proposal_id] = approved
        return approved

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = _require_proposal(self.get_proposal(proposal_id), proposal_id)
        rejected = _memory_proposals.reject_proposal(
            proposal, decided_by=decided_by, reason=reason
        )
        self._proposals[proposal_id] = rejected
        return rejected

    def search(self, query: str) -> list[FactValue]:
        return _search_facts(self._proposals.values(), query)


class LocalMemoryStore:
    """SQLite-backed local memory proposal store."""

    def __init__(self, store: LocalStore) -> None:
        self._store = store

    def propose(self, proposal: MemoryProposal) -> MemoryProposal:
        self._store.put_proposal(proposal)
        return proposal

    def get_proposal(self, proposal_id: str) -> MemoryProposal | None:
        return self._store.get_proposal(proposal_id)

    def list_proposals(
        self,
        *,
        task_id: str | None = None,
        status: str | None = None,
    ) -> list[MemoryProposal]:
        return _filter_proposals(self._store.list_proposals(), task_id=task_id, status=status)

    def approve(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = _require_proposal(self.get_proposal(proposal_id), proposal_id)
        approved = _memory_proposals.approve_proposal(
            proposal, decided_by=decided_by, reason=reason
        )
        self._store.put_proposal(approved)
        return approved

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = _require_proposal(self.get_proposal(proposal_id), proposal_id)
        rejected = _memory_proposals.reject_proposal(
            proposal, decided_by=decided_by, reason=reason
        )
        self._store.put_proposal(rejected)
        return rejected

    def search(self, query: str) -> list[FactValue]:
        return _search_facts(self._store.list_proposals(), query)

    def write_fact(self, fact: FactValue) -> FactValue:
        """Reject direct durable writes until a policy-granted path exists."""
        message = "direct local memory writes require a memory.write grant"
        raise DirectMemoryWriteDeniedError(message)


@dataclass(frozen=True)
class StigmemConfig:
    """Connection settings for a Stigmem node."""

    node_url: str
    api_key: str | None = None
    timeout_seconds: float = 5.0

    @classmethod
    def from_env(cls, env: dict[str, str]) -> StigmemConfig:
        """Load Stigmem connection settings from environment values."""
        node_url = env.get("CRAIK_STIGMEM_URL", "").strip()
        if not node_url:
            raise StigmemCapabilityError("CRAIK_STIGMEM_URL is required for Stigmem memory")
        return cls(
            node_url=node_url,
            api_key=env.get("CRAIK_STIGMEM_API_KEY"),
            timeout_seconds=float(env.get("CRAIK_STIGMEM_TIMEOUT", "5.0")),
        )


class StigmemClient:
    """Small dependency-free HTTP client for Stigmem's v0.1.0 endpoint surface."""

    def __init__(self, config: StigmemConfig) -> None:
        self._config = config
        self._base_url = config.node_url.rstrip("/")

    def health(self) -> dict[str, Any]:
        """Call `GET /healthz`."""
        payload = self._request_json("GET", "/healthz")
        return payload if isinstance(payload, dict) else {"status": "ok"}

    def metadata(self) -> dict[str, Any]:
        """Call `GET /.well-known/stigmem`."""
        payload = self._request_json("GET", "/.well-known/stigmem")
        if not isinstance(payload, dict):
            raise StigmemCapabilityError("Stigmem metadata response must be an object")
        return payload

    def list_facts(
        self,
        *,
        query: str | None = None,
        entity: str | None = None,
        relation: str | None = None,
        scope: MemoryScope | None = None,
        limit: int = 50,
    ) -> list[FactValue]:
        """Call `GET /v1/facts` and normalize returned facts."""
        params: dict[str, str] = {"limit": str(limit)}
        if query:
            params["q"] = query
        if entity:
            params["entity"] = entity
        if relation:
            params["relation"] = relation
        if scope:
            params["scope"] = scope
        payload = self._request_json("GET", "/v1/facts", params=params)
        return [_fact_from_stigmem(item) for item in _fact_items(payload)]

    def get_fact(self, fact_id: str) -> FactValue:
        """Call `GET /v1/facts/{fact_id}`."""
        payload = self._request_json("GET", f"/v1/facts/{parse.quote(fact_id, safe='')}")
        if not isinstance(payload, dict):
            raise StigmemRequestError("Stigmem fact response must be an object")
        return _fact_from_stigmem(payload)

    def get_provenance(self, fact_id: str) -> dict[str, Any]:
        """Call `GET /v1/facts/{fact_id}/provenance`."""
        payload = self._request_json(
            "GET",
            f"/v1/facts/{parse.quote(fact_id, safe='')}/provenance",
        )
        if not isinstance(payload, dict):
            raise StigmemRequestError("Stigmem provenance response must be an object")
        return payload

    def post_fact(self, fact: FactValue) -> FactValue:
        """Call `POST /v1/facts` and normalize the created fact."""
        payload = self._request_json("POST", "/v1/facts", json_body=_fact_to_stigmem(fact))
        if not isinstance(payload, dict):
            raise StigmemRequestError("Stigmem fact write response must be an object")
        return _fact_from_stigmem(payload)

    def detect_capabilities(self) -> MemoryBackendCapabilities:
        """Detect required and optional Stigmem behavior used by Craik."""
        self.health()
        metadata = self.metadata()
        self.list_facts(limit=1)
        optional = _optional_capabilities(metadata)
        return MemoryBackendCapabilities(
            backend="stigmem",
            node_url=str(metadata.get("node_url") or self._base_url),
            node_id=_optional_str(metadata.get("node_id") or metadata.get("id")),
            auth_required=_auth_required(metadata),
            required=MemoryRequiredCapabilities(
                health=True,
                metadata=True,
                fact_write=True,
                fact_query=True,
                fact_get=True,
                fact_provenance=True,
            ),
            optional=optional,
            checked_at=datetime.now(UTC),
        )

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        import json

        url = f"{self._base_url}{path}"
        if params:
            url = f"{url}?{parse.urlencode(params)}"
        body = None
        headers = {"Accept": "application/json"}
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        http_request = request.Request(url, data=body, headers=headers, method=method)
        try:
            with request.urlopen(http_request, timeout=self._config.timeout_seconds) as response:
                data = response.read()
        except error.HTTPError as exc:
            _raise_stigmem_http_error(exc)
        except error.URLError as exc:
            raise StigmemRequestError(f"Stigmem request failed: {exc.reason}") from exc
        if not data:
            return {}
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise StigmemRequestError("Stigmem response was not valid JSON") from exc


class StigmemMemoryStore:
    """Stigmem-backed memory backend with local proposal storage."""

    def __init__(
        self,
        client: StigmemClient,
        proposal_store: LocalMemoryStore | None = None,
    ) -> None:
        self._client = client
        self._proposal_store = proposal_store

    def discover(self) -> MemoryBackendCapabilities:
        """Return detected Stigmem backend capabilities."""
        return self._client.detect_capabilities()

    def propose(self, proposal: MemoryProposal) -> MemoryProposal:
        """Store proposals locally because Stigmem stores immutable facts."""
        if self._proposal_store is None:
            return proposal
        return self._proposal_store.propose(proposal)

    def get_proposal(self, proposal_id: str) -> MemoryProposal | None:
        if self._proposal_store is None:
            return None
        return self._proposal_store.get_proposal(proposal_id)

    def list_proposals(
        self,
        *,
        task_id: str | None = None,
        status: str | None = None,
    ) -> list[MemoryProposal]:
        if self._proposal_store is None:
            return []
        return self._proposal_store.list_proposals(task_id=task_id, status=status)

    def approve(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        if self._proposal_store is None:
            raise MemoryProposalNotFoundError(f"unknown memory proposal: {proposal_id}")
        return self._proposal_store.approve(proposal_id, decided_by=decided_by, reason=reason)

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        if self._proposal_store is None:
            raise MemoryProposalNotFoundError(f"unknown memory proposal: {proposal_id}")
        return self._proposal_store.reject(proposal_id, decided_by=decided_by, reason=reason)

    def search(self, query: str) -> list[FactValue]:
        return self._client.list_facts(query=query)

    def get_fact(self, fact_id: str) -> FactValue:
        return self._client.get_fact(fact_id)

    def get_provenance(self, fact_id: str) -> dict[str, Any]:
        return self._client.get_provenance(fact_id)

    def write_fact(
        self,
        fact: FactValue,
        *,
        policy: PolicyEnvelope,
        grants: list[CapabilityGrant],
    ) -> FactValue:
        """Write a fact to Stigmem only when policy grants direct memory writes."""
        decision = check_memory_grant(
            policy=policy,
            grants=grants,
            operation="write",
            target=f"scope:{fact.scope}",
        )
        if not decision.allowed:
            raise DirectMemoryWriteDeniedError(decision.reason)
        return self._client.post_fact(fact)


def build_memory_diff(
    *,
    task_id: str,
    proposals: Iterable[MemoryProposal],
    facts_written: Iterable[MemoryFactReference] = (),
    write_failures: Iterable[MemoryWriteFailure] = (),
    facts_read: Iterable[MemoryFactReference] = (),
) -> MemoryDiff:
    """Build a run-scoped memory diff from proposal and fact activity."""
    scoped = [proposal for proposal in proposals if proposal.task_id == task_id]
    return MemoryDiff(
        id=f"memdiff_{task_id}",
        task_id=task_id,
        proposals_created=sorted(proposal.id for proposal in scoped),
        proposals_approved=sorted(
            proposal.id for proposal in scoped if proposal.status == "approved"
        ),
        proposals_rejected=sorted(
            proposal.id for proposal in scoped if proposal.status == "rejected"
        ),
        facts_written=sorted(facts_written, key=_fact_reference_sort_key),
        write_failures=sorted(
            write_failures,
            key=lambda failure: _fact_reference_sort_key(failure.fact),
        ),
        facts_read=sorted(facts_read, key=_fact_reference_sort_key),
        created_at=datetime.now(UTC),
    )


def preview_memory_impact(
    *,
    task_id: str,
    proposals: Iterable[MemoryProposal],
    existing_facts: Iterable[FactValue],
) -> MemoryImpactPreview:
    """Preview memory additions, invalidations, evidence gaps, and likely contradictions."""
    scoped = [proposal for proposal in proposals if proposal.task_id == task_id]
    additions = [
        fact_reference(proposal.fact)
        for proposal in scoped
        if proposal.operation in {"add", "update"}
    ]
    invalidations = [
        fact_reference(proposal.fact) for proposal in scoped if proposal.operation == "invalidate"
    ]
    evidence_missing = sorted(proposal.id for proposal in scoped if not proposal.evidence)
    contradictions = _likely_contradictions(scoped, existing_facts)
    return MemoryImpactPreview(
        id=f"mempreview_{task_id}",
        task_id=task_id,
        facts_to_add=sorted(additions, key=_fact_reference_sort_key),
        facts_to_invalidate=sorted(invalidations, key=_fact_reference_sort_key),
        likely_contradictions=contradictions,
        evidence_missing=evidence_missing,
        scope_summary=_scope_summary(scoped),
        created_at=datetime.now(UTC),
    )


def fact_reference(
    fact: FactValue,
    *,
    fact_id: str | None = None,
    cid: str | None = None,
) -> MemoryFactReference:
    """Create a redacted fact reference for diffs and previews."""
    return MemoryFactReference(
        id=fact_id,
        cid=cid,
        entity=str(redact(fact.entity).value),
        relation=str(redact(fact.relation).value),
        value=str(redact(fact.value).value),
        source=str(redact(fact.source).value),
        scope=fact.scope,
        trust_class=fact.trust_class,
    )


def memory_write_failure(
    *,
    fact: FactValue,
    reason: str,
) -> MemoryWriteFailure:
    """Create a redacted memory write failure record."""
    return MemoryWriteFailure(
        fact=fact_reference(fact),
        reason=str(redact(reason).value),
        attempted_at=datetime.now(UTC),
    )


def _filter_proposals(
    proposals: list[MemoryProposal],
    *,
    task_id: str | None,
    status: str | None,
) -> list[MemoryProposal]:
    filtered = proposals
    if task_id is not None:
        filtered = [proposal for proposal in filtered if proposal.task_id == task_id]
    if status is not None:
        filtered = [proposal for proposal in filtered if proposal.status == status]
    return sorted(filtered, key=lambda proposal: proposal.id)


def _search_facts(proposals: Iterable[MemoryProposal], query: str) -> list[FactValue]:
    needle = query.lower()
    facts: list[FactValue] = []
    for proposal in proposals:
        if proposal.status != "approved":
            continue
        haystack = " ".join(
            (
                proposal.fact.entity,
                proposal.fact.relation,
                proposal.fact.value,
                proposal.fact.source,
            )
        ).lower()
        if needle in haystack:
            facts.append(proposal.fact)
    return sorted(facts, key=lambda fact: (fact.entity, fact.relation, fact.source))


def _likely_contradictions(
    proposals: Iterable[MemoryProposal],
    existing_facts: Iterable[FactValue],
) -> list[MemoryContradictionPreview]:
    existing_by_key: dict[tuple[str, str], list[FactValue]] = {}
    for fact in existing_facts:
        existing_by_key.setdefault((fact.entity, fact.relation), []).append(fact)

    contradictions: list[MemoryContradictionPreview] = []
    for proposal in proposals:
        if proposal.operation == "invalidate":
            continue
        for existing in existing_by_key.get((proposal.fact.entity, proposal.fact.relation), []):
            if existing.value == proposal.fact.value:
                continue
            contradictions.append(
                MemoryContradictionPreview(
                    entity=proposal.fact.entity,
                    relation=proposal.fact.relation,
                    existing_value=existing.value,
                    proposed_value=proposal.fact.value,
                    reason="same entity and relation with a different value",
                )
            )
    return sorted(
        contradictions,
        key=lambda item: (item.entity, item.relation, item.existing_value, item.proposed_value),
    )


def _scope_summary(proposals: Iterable[MemoryProposal]) -> dict[MemoryScope, int]:
    summary: dict[MemoryScope, int] = {}
    for proposal in proposals:
        summary[proposal.fact.scope] = summary.get(proposal.fact.scope, 0) + 1
    return dict(sorted(summary.items()))


def _fact_reference_sort_key(fact: MemoryFactReference) -> tuple[str, str, str, str]:
    return (fact.entity, fact.relation, fact.value, fact.source)


def _require_proposal(proposal: MemoryProposal | None, proposal_id: str) -> MemoryProposal:
    if proposal is None:
        raise MemoryProposalNotFoundError(f"unknown memory proposal: {proposal_id}")
    return proposal


def _raise_stigmem_http_error(exc: error.HTTPError) -> None:
    if exc.code == 401:
        raise StigmemAuthError("Stigmem authentication failed") from exc
    if exc.code == 403:
        raise StigmemPermissionError("Stigmem permission denied") from exc
    raise StigmemRequestError(f"Stigmem request failed with HTTP {exc.code}") from exc


def _fact_to_stigmem(fact: FactValue) -> dict[str, Any]:
    return {
        "entity": str(redact(fact.entity).value),
        "relation": str(redact(fact.relation).value),
        "value": {"type": "text", "v": str(redact(fact.value).value)},
        "source": str(redact(fact.source).value),
        "confidence": fact.confidence,
        "scope": fact.scope,
        "trust_class": fact.trust_class,
    }


def _fact_from_stigmem(payload: dict[str, Any]) -> FactValue:
    value = payload.get("value", "")
    if isinstance(value, dict):
        value_text = str(value.get("v", ""))
    else:
        value_text = str(value)
    return FactValue(
        entity=str(payload.get("entity", "")),
        relation=str(payload.get("relation", "")),
        value=value_text,
        source=str(payload.get("source", "")),
        confidence=float(payload.get("confidence", 0.0)),
        scope=_memory_scope_from_payload(payload.get("scope")),
        trust_class=_trust_class_from_payload(payload.get("trust_class")),
    )


def _fact_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("facts", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    raise StigmemRequestError("Stigmem facts response must be a list or object with facts")


def _optional_capabilities(metadata: dict[str, Any]) -> MemoryOptionalCapabilities:
    return MemoryOptionalCapabilities(
        recall=bool(metadata.get("recall", False)),
        conflicts=bool(metadata.get("conflicts", False)),
        source_attestation=_source_attestation_mode(metadata.get("source_attestation")),
        federation=bool(metadata.get("federation", False)),
    )


def _auth_required(metadata: dict[str, Any]) -> bool:
    auth = metadata.get("auth")
    if isinstance(auth, dict):
        return bool(auth.get("required", False))
    if isinstance(auth, str):
        return auth not in {"none", "off", "disabled"}
    return False


def _source_attestation_mode(value: Any) -> LiteralSourceAttestation:
    if value in {"warn", "enforce", "off"}:
        return cast(LiteralSourceAttestation, value)
    return "off"


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _memory_scope_from_payload(value: Any) -> MemoryScope:
    if value in {"local", "team", "company", "public"}:
        return cast(MemoryScope, value)
    return "team"


def _trust_class_from_payload(value: Any) -> TrustClass:
    if value in {"observed", "reported", "inferred", "policy", "external", "stale-risk"}:
        return cast(TrustClass, value)
    return "reported"


create_proposal = _memory_proposals.create_proposal
approve_proposal = _memory_proposals.approve_proposal
reject_proposal = _memory_proposals.reject_proposal
proposal_id = _memory_proposals.proposal_id
evidence_reference = _memory_proposals.evidence_reference
MemoryError = _memory_errors.MemoryError
EvidenceRequiredError = _memory_errors.EvidenceRequiredError
