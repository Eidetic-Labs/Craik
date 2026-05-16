import pytest
from pydantic import ValidationError

from craik.contracts.models import PluginDescriptor
from craik.runtime.paths import ensure_craik_home
from craik.runtime.store import LocalStore


def _descriptor(**overrides: object) -> PluginDescriptor:
    payload = {
        "id": "plugin_docs_reconcile",
        "name": "Docs Reconcile Plugin",
        "plugin_version": "0.1.0",
        "description": "Adds governed docs reconciliation workflow entrypoints.",
        "publisher": "Eidetic Labs",
        "entrypoints": [
            {
                "id": "entry_workflow",
                "kind": "workflow",
                "path": "plugin.py:run",
                "description": "Runs the docs reconciliation workflow.",
            }
        ],
        "capabilities": [
            {
                "capability": "repo.read",
                "description": "Read project source and documentation files.",
                "required": True,
                "grant_required": True,
                "risk": "medium",
                "operations": ["read"],
                "targets": ["repo"],
            }
        ],
        "docs": ["README.md", "docs/plugin.md"],
        "compatibility": {
            "craik_versions": ["0.7"],
            "python_versions": ["3.12"],
            "platforms": ["darwin", "linux"],
            "status": "supported",
            "notes": "Fixture descriptor for contract validation.",
        },
        "security_notes": [
            "Descriptor declares capability needs only; runtime authority requires grants."
        ],
        "skill_package_ids": ["skill_docs_reconcile"],
        "provenance_ids": ["evidence_plugin_descriptor"],
        "runtime_authority": False,
        "created_at": "2026-05-16T15:45:00Z",
    }
    payload.update(overrides)
    return PluginDescriptor.model_validate(payload)


def test_plugin_descriptor_round_trips_in_store(tmp_path) -> None:
    paths = ensure_craik_home({"CRAIK_HOME": str(tmp_path / "home")})
    store = LocalStore.from_paths(paths)
    store.initialize()
    try:
        descriptor = _descriptor()
        store.put_plugin_descriptor(descriptor)

        assert store.get_plugin_descriptor(descriptor.id) == descriptor
        assert store.list_plugin_descriptors() == [descriptor]
        assert descriptor.runtime_authority is False
    finally:
        store.close()


def test_plugin_descriptor_requires_capabilities() -> None:
    with pytest.raises(ValidationError):
        _descriptor(capabilities=[])


def test_plugin_descriptor_requires_security_and_compatibility_metadata() -> None:
    with pytest.raises(ValidationError):
        _descriptor(security_notes=[])

    with pytest.raises(ValidationError):
        _descriptor(compatibility={"status": "supported"})


def test_plugin_descriptor_requires_versioned_identity() -> None:
    with pytest.raises(ValidationError, match="semantic-version-like"):
        _descriptor(plugin_version="preview")


def test_plugin_descriptor_separates_authority_from_declarations() -> None:
    with pytest.raises(ValidationError):
        _descriptor(runtime_authority=True)

    with pytest.raises(ValidationError, match="explicit grants"):
        _descriptor(
            capabilities=[
                {
                    "capability": "repo.write",
                    "description": "Write project files.",
                    "required": True,
                    "grant_required": False,
                    "risk": "high",
                    "operations": ["write"],
                    "targets": ["repo"],
                }
            ]
        )
