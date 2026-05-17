"""Operator-bound policy checks."""

from __future__ import annotations

from craik.contracts.models import PolicyEnvelope
from craik.runtime.policy.policy import GrantDecision


def check_operator_policy(
    *,
    policy: PolicyEnvelope,
    operator_subject: str | None,
    operator_issuer: str | None,
    operator_groups: list[str],
) -> GrantDecision:
    """Evaluate policy-level operator identity requirements."""
    capability = "operator.identity"
    metadata = _operator_policy_metadata(policy)
    if not metadata:
        return GrantDecision(
            allowed=True,
            capability=capability,
            target="operator:any",
            reason="operator identity is not restricted by policy",
        )

    target = operator_subject or "operator:none"
    reason = _operator_denial_reason(
        policy=policy,
        operator_subject=operator_subject,
        operator_issuer=operator_issuer,
        operator_groups=operator_groups,
    )
    if reason is not None:
        return GrantDecision(
            allowed=False,
            capability=capability,
            target=target,
            reason=reason,
            receipt_metadata={**metadata, "policy_id": policy.id},
        )

    metadata["matched_operator_group"] = _matched_operator_group(
        policy.allowed_operator_groups,
        operator_groups,
    )
    return GrantDecision(
        allowed=True,
        capability=capability,
        target=target,
        reason="operator identity allowed by policy",
        receipt_metadata=metadata,
    )


def _operator_denial_reason(
    *,
    policy: PolicyEnvelope,
    operator_subject: str | None,
    operator_issuer: str | None,
    operator_groups: list[str],
) -> str | None:
    if operator_subject is None:
        return "operator identity required by policy; run craik login"
    if policy.required_operator_issuer and operator_issuer != policy.required_operator_issuer:
        return "operator issuer denied by policy"
    if (
        policy.allowed_operator_subjects is not None
        and operator_subject not in policy.allowed_operator_subjects
    ):
        return "operator subject denied by policy"
    if (
        policy.allowed_operator_groups is not None
        and _matched_operator_group(policy.allowed_operator_groups, operator_groups) is None
    ):
        return "operator groups denied by policy"
    return None


def _operator_policy_metadata(policy: PolicyEnvelope) -> dict[str, object]:
    if not (
        policy.required_operator
        or policy.allowed_operator_groups is not None
        or policy.allowed_operator_subjects is not None
        or policy.required_operator_issuer is not None
    ):
        return {}
    return {
        "policy_id": policy.id,
        "required_operator": policy.required_operator,
        "allowed_operator_groups": list(policy.allowed_operator_groups or []),
        "allowed_operator_subjects": list(policy.allowed_operator_subjects or []),
        "required_operator_issuer": policy.required_operator_issuer,
    }


def _matched_operator_group(
    allowed_groups: list[str] | None,
    operator_groups: list[str],
) -> str | None:
    if allowed_groups is None:
        return None
    operator_group_set = set(operator_groups)
    return next((group for group in allowed_groups if group in operator_group_set), None)
