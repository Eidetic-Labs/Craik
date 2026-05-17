"""Secret migration policy for import workflows."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from craik.contracts.models import CraikModel

SecretMigrationHandling = Literal["redact", "reference", "reconfigure", "block"]
SecretMigrationDecisionStatus = Literal[
    "allowed",
    "redacted",
    "referenced",
    "operator_reconfiguration_required",
    "blocked",
]


class SecretMigrationPolicyRule(CraikModel):
    """Policy for one source field that may contain secret material."""

    source_field: str
    handling: SecretMigrationHandling
    reason: str
    dry_run_warning: str
    requires_operator_action: bool = False
    receipt_required: bool = True

    @model_validator(mode="after")
    def validate_rule(self) -> SecretMigrationPolicyRule:
        """Keep secret handling auditable."""
        if self.handling in {"reconfigure", "block"} and not self.requires_operator_action:
            raise ValueError("reconfigure and block secret rules require operator action")
        if self.handling != "redact" and not self.receipt_required:
            raise ValueError("non-redaction secret rules require receipts")
        if not self.reason:
            raise ValueError("secret migration rules require reason")
        if not self.dry_run_warning:
            raise ValueError("secret migration rules require dry_run_warning")
        return self


class SecretMigrationPolicy(CraikModel):
    """Policy describing how migration handles source secrets."""

    id: str
    source_name: str
    rules: list[SecretMigrationPolicyRule] = Field(min_length=1)
    default_secret_handling: Literal["block"] = "block"
    prohibited_behavior: str = "copy_secret_value"
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_policy(self) -> SecretMigrationPolicy:
        """Ensure the policy cannot authorize secret copying."""
        if self.prohibited_behavior != "copy_secret_value":
            raise ValueError("secret migration policy must prohibit secret value copying")
        if self.default_secret_handling != "block":
            raise ValueError("unknown secret fields must be blocked by default")
        if not self.policy_envelope_id:
            raise ValueError("secret migration policies require policy_envelope_id")
        return self


class SecretMigrationDecision(CraikModel):
    """Decision produced for one import field under a secret migration policy."""

    source_field: str
    status: SecretMigrationDecisionStatus
    warning: str | None = None
    reason: str | None = None
    policy_id: str
    policy_envelope_id: str
    evidence_ids: list[str] = Field(min_length=1)
    receipt_ids: list[str] = Field(default_factory=list)
    contains_secret: bool
    copied_secret_value: Literal[False] = False
    requires_operator_action: bool = False

    @model_validator(mode="after")
    def validate_decision(self) -> SecretMigrationDecision:
        """Require receipts for every secret migration decision."""
        if self.contains_secret and not self.receipt_ids:
            raise ValueError("secret migration decisions require receipts")
        if self.status == "allowed" and self.contains_secret:
            raise ValueError("secret fields cannot be allowed without safe handling")
        if self.status in {"operator_reconfiguration_required", "blocked"}:
            if not self.requires_operator_action:
                raise ValueError("blocked and reconfiguration decisions require operator action")
        return self


def evaluate_secret_migration(
    *,
    source_field: str,
    contains_secret: bool,
    policy: SecretMigrationPolicy,
) -> SecretMigrationDecision:
    """Evaluate a source field under a secret migration policy."""
    if not contains_secret:
        return SecretMigrationDecision(
            source_field=source_field,
            status="allowed",
            policy_id=policy.id,
            policy_envelope_id=policy.policy_envelope_id,
            evidence_ids=policy.evidence_ids,
            contains_secret=False,
        )

    rule = next((item for item in policy.rules if item.source_field == source_field), None)
    if rule is None:
        return SecretMigrationDecision(
            source_field=source_field,
            status="blocked",
            warning="secret field has no migration policy rule",
            reason="unknown secret fields are blocked by default",
            policy_id=policy.id,
            policy_envelope_id=policy.policy_envelope_id,
            evidence_ids=policy.evidence_ids,
            receipt_ids=policy.receipt_ids,
            contains_secret=True,
            requires_operator_action=True,
        )

    return SecretMigrationDecision(
        source_field=source_field,
        status=_decision_status(rule.handling),
        warning=rule.dry_run_warning,
        reason=rule.reason,
        policy_id=policy.id,
        policy_envelope_id=policy.policy_envelope_id,
        evidence_ids=policy.evidence_ids,
        receipt_ids=policy.receipt_ids if rule.receipt_required else [],
        contains_secret=True,
        requires_operator_action=rule.requires_operator_action,
    )


def _decision_status(handling: SecretMigrationHandling) -> SecretMigrationDecisionStatus:
    if handling == "redact":
        return "redacted"
    if handling == "reference":
        return "referenced"
    if handling == "reconfigure":
        return "operator_reconfiguration_required"
    return "blocked"
