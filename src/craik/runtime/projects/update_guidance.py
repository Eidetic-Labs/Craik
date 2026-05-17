"""Update guidance without self-modifying behavior."""

from __future__ import annotations

from craik.runtime.store import CURRENT_MIGRATION

SUPPORTED_PYTHON = ">=3.12"


def update_guidance_payload(*, installed_version: str) -> dict[str, object]:
    """Return inspectable update guidance for the current installation."""
    return {
        "installed_version": installed_version,
        "supported_python": SUPPORTED_PYTHON,
        "local_store_migration": CURRENT_MIGRATION,
        "self_update_supported": False,
        "compatibility": {
            "contracts": "0.1.0",
            "local_store_migration": CURRENT_MIGRATION,
        },
        "steps": [
            "Review release notes and migration notes before updating.",
            "Run craik doctor before changing the installation.",
            "Update Craik with the package manager or source checkout that installed it.",
            "Run craik doctor after updating.",
            "Run project validation before starting the gateway.",
        ],
        "boundaries": [
            "Craik does not rewrite its own installation.",
            "Craik does not migrate local state without explicit future migration commands.",
            "Craik does not fetch remote release metadata during update guidance.",
        ],
    }
