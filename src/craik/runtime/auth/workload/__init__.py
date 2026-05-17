"""Workload identity providers for OIDC federation."""

from craik.runtime.auth.workload.oidc_federation import (
    EnvVarTokenIdentity,
    GenericFileTokenIdentity,
    GitHubActionsWorkloadIdentity,
    KubernetesProjectedTokenIdentity,
    WorkloadIdentityError,
    WorkloadIdentityProvider,
)

__all__ = [
    "EnvVarTokenIdentity",
    "GenericFileTokenIdentity",
    "GitHubActionsWorkloadIdentity",
    "KubernetesProjectedTokenIdentity",
    "WorkloadIdentityError",
    "WorkloadIdentityProvider",
]
