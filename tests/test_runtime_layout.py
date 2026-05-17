import importlib
from pathlib import Path


def test_runtime_subpackages_stay_below_sibling_module_limit() -> None:
    runtime_root = Path(__file__).parents[1] / "src" / "craik" / "runtime"
    package_dirs = [
        runtime_root,
        *(path for path in runtime_root.iterdir() if path.is_dir() and path.name != "__pycache__"),
    ]

    oversized = {
        path.relative_to(runtime_root).as_posix() or ".": len(list(path.glob("*.py")))
        for path in package_dirs
        if len(list(path.glob("*.py"))) > 15
    }

    assert oversized == {}


def test_runtime_legacy_module_imports_resolve_to_new_packages() -> None:
    legacy_handoffs = importlib.import_module("craik.runtime.handoffs")
    new_handoffs = importlib.import_module("craik.runtime.work.handoffs")
    legacy_provider_runtime = importlib.import_module("craik.runtime.provider_runtime")
    new_provider_runtime = importlib.import_module("craik.runtime.providers.provider_runtime")

    assert legacy_handoffs is new_handoffs
    assert legacy_provider_runtime is new_provider_runtime
