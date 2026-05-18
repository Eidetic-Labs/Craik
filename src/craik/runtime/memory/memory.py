"""Memory backend interfaces and local proposal flow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Literal, cast
from urllib import error, parse, request

from craik.contracts.models import (
    CapabilityGrant,
    FactValue,
    MemoryBackendCapabilities,
    MemoryOptionalCapabilities,
    MemoryProposal,
    MemoryRequiredCapabilities,
    MemoryScope,
    PolicyEnvelope,
    TrustClass,
)
from craik.runtime.memory import memory_errors as _memory_errors
from craik.runtime.memory import memory_proposals as _memory_proposals
from craik.runtime.memory.diff import (
    build_memory_diff as build_memory_diff,
)
from craik.runtime.memory.diff import (
    fact_reference as fact_reference,
)
from craik.runtime.memory.diff import (
    memory_write_failure as memory_write_failure,
)
from craik.runtime.memory.diff import (
    preview_memory_impact as preview_memory_impact,
)
from craik.runtime.memory.local_stores import (
    EphemeralMemoryStore as EphemeralMemoryStore,
)
from craik.runtime.memory.local_stores import (
    LocalMemoryStore as LocalMemoryStore,
)
from craik.runtime.memory.local_stores import (
    MemoryStore as MemoryStore,
)
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

LiteralSourceAttestation = Literal["warn", "enforce", "off"]


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


if not TYPE_CHECKING:
    __all__ = [name for name in globals() if not name.startswith("_")]
