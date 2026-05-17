"""Memory runtime exception types."""

from __future__ import annotations


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
