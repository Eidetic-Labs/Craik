"""Memory backend interfaces and local proposal flow."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, Protocol, cast
from urllib import error, parse, request

from craik.contracts.models import (
    CapabilityGrant,
    EvidenceReference,
    FactValue,
    MemoryBackendCapabilities,
    MemoryOptionalCapabilities,
    MemoryProposal,
    MemoryRequiredCapabilities,
    MemoryScope,
    PolicyEnvelope,
    ProposalOperation,
    TrustClass,
)
from craik.runtime.policy import check_memory_grant
from craik.runtime.redaction import redact
from craik.runtime.store import LocalStore

LiteralSourceAttestation = Literal["warn", "enforce", "off"]


class MemoryError(RuntimeError):
    """Base error for memory backend failures."""


class MemoryProposalNotFoundError(MemoryError):
    """Raised when a proposal cannot be found."""


class EvidenceRequiredError(MemoryError):
    """Raised when promotion is attempted without evidence."""


class DirectMemoryWriteDeniedError(MemoryError):
    """Raised when direct writes are attempted without a policy grant."""


class StigmemAuthError(MemoryError):
    """Raised when a Stigmem node rejects authentication."""


class StigmemPermissionError(MemoryError):
    """Raised when a Stigmem node rejects an authorized action."""


class StigmemRequestError(MemoryError):
    """Raised when a Stigmem request fails."""


class StigmemCapabilityError(MemoryError):
    """Raised when a Stigmem node lacks required v0.1.0 compatibility."""


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
        approved = approve_proposal(proposal, decided_by=decided_by, reason=reason)
        self._proposals[proposal_id] = approved
        return approved

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = _require_proposal(self.get_proposal(proposal_id), proposal_id)
        rejected = reject_proposal(proposal, decided_by=decided_by, reason=reason)
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
        approved = approve_proposal(proposal, decided_by=decided_by, reason=reason)
        self._store.put_proposal(approved)
        return approved

    def reject(self, proposal_id: str, *, decided_by: str, reason: str) -> MemoryProposal:
        proposal = _require_proposal(self.get_proposal(proposal_id), proposal_id)
        rejected = reject_proposal(proposal, decided_by=decided_by, reason=reason)
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


def create_proposal(
    *,
    task_id: str,
    entity: str,
    relation: str,
    value: str,
    source: str,
    confidence: float,
    scope: MemoryScope,
    trust_class: TrustClass,
    evidence: list[EvidenceReference],
    operation: ProposalOperation = "add",
) -> MemoryProposal:
    """Create a redacted reviewable memory proposal."""
    fact = FactValue(
        entity=str(redact(entity).value),
        relation=str(redact(relation).value),
        value=str(redact(value).value),
        source=str(redact(source).value),
        confidence=confidence,
        scope=scope,
        trust_class=trust_class,
    )
    return MemoryProposal(
        id=proposal_id(task_id, entity, relation),
        task_id=task_id,
        operation=operation,
        fact=fact,
        evidence=evidence,
        requires_approval=True,
        status="pending",
    )


def approve_proposal(
    proposal: MemoryProposal,
    *,
    decided_by: str,
    reason: str,
) -> MemoryProposal:
    """Approve a proposal after enforcing evidence requirements."""
    if not proposal.evidence:
        raise EvidenceRequiredError(f"proposal {proposal.id} requires evidence before approval")
    return proposal.model_copy(
        update={
            "status": "approved",
            "decision_reason": reason,
            "decided_by": decided_by,
            "decided_at": datetime.now(UTC),
        }
    )


def reject_proposal(
    proposal: MemoryProposal,
    *,
    decided_by: str,
    reason: str,
) -> MemoryProposal:
    """Reject a proposal with reviewer context."""
    return proposal.model_copy(
        update={
            "status": "rejected",
            "decision_reason": reason,
            "decided_by": decided_by,
            "decided_at": datetime.now(UTC),
        }
    )


def proposal_id(task_id: str, entity: str, relation: str) -> str:
    """Create a stable proposal id."""
    return f"memprop_{task_id.removeprefix('task_')}_{_slug(entity)}_{_slug(relation)}"


def evidence_reference(
    *,
    task_id: str,
    source: str,
    locator: str,
    summary: str,
) -> EvidenceReference:
    """Create an evidence reference for a memory proposal."""
    return EvidenceReference(
        id=f"evidence_{task_id}_{_slug(source)}_{_slug(locator)}",
        source=str(redact(source).value),
        kind="other",
        locator=str(redact(locator).value),
        summary=str(redact(summary).value),
        captured_at=datetime.now(UTC),
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


def _require_proposal(proposal: MemoryProposal | None, proposal_id: str) -> MemoryProposal:
    if proposal is None:
        raise MemoryProposalNotFoundError(f"unknown memory proposal: {proposal_id}")
    return proposal


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "value"


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
