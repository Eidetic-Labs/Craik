"""Policy regression harness for release gates."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from craik.contracts.models import DocsProfile, FactValue
from craik.runtime.memory import (
    DirectMemoryWriteDeniedError,
    LocalMemoryStore,
    create_proposal,
    evidence_reference,
)
from craik.runtime.policy import (
    check_file_write_grant,
    check_memory_grant,
    check_shell_grant,
    fail_open_receipt,
    generate_policy_envelope,
)
from craik.runtime.redaction import contains_unredacted_secret, redact
from craik.runtime.store import LocalStore


@dataclass(frozen=True)
class PolicyTestResult:
    """One policy regression check result."""

    name: str
    status: str
    message: str
    details: dict[str, Any]

    def to_payload(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True)
class PolicyTestReport:
    """Machine-readable policy regression report."""

    schema: str
    version: str
    status: str
    results: list[PolicyTestResult]

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "version": self.version,
            "status": self.status,
            "results": [result.to_payload() for result in self.results],
            "summary": {
                "passed": sum(result.status == "passed" for result in self.results),
                "failed": sum(result.status == "failed" for result in self.results),
                "total": len(self.results),
            },
        }


class PolicyTestHarness:
    """Run policy regression checks required for v0.1.0."""

    def __init__(self, store: LocalStore) -> None:
        self.store = store

    def run(self) -> PolicyTestReport:
        checks: tuple[tuple[str, Callable[[], dict[str, Any]]], ...] = (
            ("immutable_path_requires_override_and_grant", self._immutable_path),
            ("memory_writes_become_proposals", self._memory_writes_become_proposals),
            ("trusted_local_fail_open_receipts", self._trusted_local_fail_open_receipts),
            ("automation_fails_closed", self._automation_fails_closed),
            ("runner_grant_boundary_placeholder", self._runner_grant_boundary_placeholder),
            ("redaction_receipts_logs_handoffs_case_files", self._redaction_boundaries),
        )
        results = [_run_check(name, check) for name, check in checks]
        status = "passed" if all(result.status == "passed" for result in results) else "failed"
        return PolicyTestReport(
            schema="craik.policy_test_report",
            version="0.1.0",
            status=status,
            results=results,
        )

    def _immutable_path(self) -> dict[str, Any]:
        policy = generate_policy_envelope(task_id="task_policy_test", actor="agent:policy-test")
        docs = DocsProfile(paths=["docs/"], immutable_paths=["docs/adr/"])
        no_override = check_file_write_grant(
            policy=policy,
            grants=[],
            path="docs/adr/0001-record.md",
            docs=docs,
        )
        with_override = check_file_write_grant(
            policy=policy,
            grants=[],
            path="docs/adr/0001-record.md",
            docs=docs,
            override={"approved_by": "user:maintainer", "reason": "Policy regression test."},
        )
        _assert(not no_override.allowed, "immutable write without override was allowed")
        _assert(no_override.immutable_path, "immutable path was not identified")
        _assert(not with_override.allowed, "immutable write without grant was allowed")
        _assert(with_override.approval_required, "immutable grant denial did not require approval")
        return {
            "immutable_path": "docs/adr/0001-record.md",
            "no_override_reason": no_override.reason,
            "with_override_reason": with_override.reason,
        }

    def _memory_writes_become_proposals(self) -> dict[str, Any]:
        policy = generate_policy_envelope(task_id="task_policy_test", actor="agent:policy-test")
        decision = check_memory_grant(
            policy=policy,
            grants=[],
            operation="write",
            target="scope:team",
        )
        _assert(not decision.allowed, "direct memory write was allowed without grant")
        evidence = evidence_reference(
            task_id="task_policy_test",
            source="policy-test",
            locator="memory-writes-become-proposals",
            summary="Policy regression evidence.",
        )
        proposal = create_proposal(
            task_id="task_policy_test",
            entity="repo:Eidetic-Labs/Craik",
            relation="craik:policy_test",
            value="Memory updates are proposed before durable write.",
            source="policy-test",
            confidence=0.9,
            scope="team",
            trust_class="policy",
            evidence=[evidence],
        )
        persisted = LocalMemoryStore(self.store).propose(proposal)
        try:
            LocalMemoryStore(self.store).write_fact(
                FactValue(
                    entity="repo:Eidetic-Labs/Craik",
                    relation="craik:policy_test",
                    value="Direct local write should be denied.",
                    source="policy-test",
                    confidence=0.9,
                    scope="team",
                    trust_class="policy",
                )
            )
        except DirectMemoryWriteDeniedError as error:
            denial = str(error)
        else:
            raise AssertionError("direct local memory write did not raise denial")
        return {
            "proposal_id": persisted.id,
            "proposal_status": persisted.status,
            "direct_write_denial": denial,
        }

    def _trusted_local_fail_open_receipts(self) -> dict[str, Any]:
        policy = generate_policy_envelope(
            task_id="task_policy_test",
            actor="agent:policy-test",
            profile="trusted-local",
            trusted_local_fail_open=True,
        )
        receipt = fail_open_receipt(
            task_id=policy.task_id,
            actor=policy.actor,
            target=policy.profile,
            reason="Policy regression test selected trusted-local.",
        )
        _assert(policy.fail_open, "trusted-local policy did not fail open")
        _assert(receipt.fail_open, "fail-open receipt did not mark fail_open")
        _assert(receipt.redacted, "fail-open receipt was not marked redacted")
        _assert(receipt.capability == "policy.fail_open", "fail-open receipt capability changed")
        return {
            "policy_id": policy.id,
            "receipt_id": receipt.id,
            "receipt_status": receipt.result.status,
        }

    def _automation_fails_closed(self) -> dict[str, Any]:
        policy = generate_policy_envelope(
            task_id="task_policy_test",
            actor="agent:ci",
            profile="automation",
        )
        shell = check_shell_grant(policy=policy, grants=[], command="pytest")
        memory = check_memory_grant(
            policy=policy,
            grants=[],
            operation="write",
            target="scope:team",
        )
        _assert(not policy.fail_open, "automation policy was fail-open")
        _assert("memory.write" in policy.denied_capabilities, "automation allows memory.write")
        _assert(
            "shell.unbounded" in policy.denied_capabilities,
            "automation allows unbounded shell",
        )
        _assert(not shell.allowed, "automation shell was allowed without grant")
        _assert(not memory.allowed, "automation memory write was allowed without grant")
        return {
            "policy_id": policy.id,
            "shell_denial": shell.reason,
            "memory_denial": memory.reason,
        }

    def _runner_grant_boundary_placeholder(self) -> dict[str, Any]:
        return {
            "status": "placeholder",
            "expected_boundary": (
                "runner adapters must call policy grant checks before side effects"
            ),
            "tracked_until": "runner adapters are implemented",
        }

    def _redaction_boundaries(self) -> dict[str, Any]:
        payloads = {
            "receipt": {
                "schema": "craik.capability_receipt",
                "result": {"summary": "Authorization: Bearer redactionfixture123"},
            },
            "log": {"line": "api_key=redactionfixture123"},
            "handoff": {
                "schema": "craik.handoff",
                "commands_run": ["curl https://user:redactionfixture123@example.com/path"],
            },
            "case_file": {
                "schema": "craik.case_file",
                "repo_state": {"remote": "https://user:redactionfixture123@example.com/repo.git"},
            },
        }
        redacted = {name: redact(payload).value for name, payload in payloads.items()}
        _assert(
            not contains_unredacted_secret(redacted),
            "redacted policy payloads still contain secret-like material",
        )
        return {
            "payloads_checked": sorted(payloads),
            "redacted": True,
        }


def _run_check(name: str, check: Callable[[], dict[str, Any]]) -> PolicyTestResult:
    try:
        details = check()
    except AssertionError as error:
        return PolicyTestResult(
            name=name,
            status="failed",
            message=str(error),
            details={},
        )
    return PolicyTestResult(
        name=name,
        status="passed",
        message="Policy regression passed.",
        details=details,
    )


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
