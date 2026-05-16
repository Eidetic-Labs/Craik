"""Read-only diagnostics for Craik local and gateway readiness."""

from __future__ import annotations

from dataclasses import dataclass

from craik.contracts.models import GatewayConfig
from craik.runtime.paths import CraikPaths
from craik.runtime.store import DATABASE_NAME, LocalStore, LocalStoreError

DiagnosticStatus = str


@dataclass(frozen=True)
class DiagnosticCheck:
    """One read-only diagnostic check result."""

    name: str
    status: DiagnosticStatus
    summary: str
    action: str | None = None

    def to_payload(self) -> dict[str, str | None]:
        """Return a JSON-ready diagnostic payload."""
        return {
            "name": self.name,
            "status": self.status,
            "summary": self.summary,
            "action": self.action,
        }


def run_doctor(paths: CraikPaths, *, env: dict[str, str]) -> dict[str, object]:
    """Run read-only diagnostics without creating local state."""
    checks = [_home_check(paths), *_store_checks(paths), _memory_backend_check(env)]
    store = _open_existing_store(paths)
    if store is None:
        checks.extend(
            [
                DiagnosticCheck(
                    name="gateway_config",
                    status="warning",
                    summary=(
                        "Gateway configuration is not inspectable because the local "
                        "store is missing."
                    ),
                    action="Run craik setup.",
                ),
                DiagnosticCheck(
                    name="gateway_prerequisites",
                    status="warning",
                    summary=(
                        "Gateway prerequisites cannot be checked without gateway "
                        "configuration."
                    ),
                    action="Run craik setup.",
                ),
                DiagnosticCheck(
                    name="policy",
                    status="warning",
                    summary="Policy readiness cannot be checked without gateway configuration.",
                    action="Run craik setup or persist a gateway policy envelope.",
                ),
            ]
        )
    else:
        try:
            config = store.get_gateway_config("gateway_default")
            checks.extend(_gateway_checks(config))
        finally:
            store.close()
    return {
        "status": _overall_status(checks),
        "checks": [check.to_payload() for check in checks],
    }


def _home_check(paths: CraikPaths) -> DiagnosticCheck:
    if paths.home.exists():
        return DiagnosticCheck(
            name="local_home",
            status="pass",
            summary=f"Craik home exists at {paths.home}.",
        )
    return DiagnosticCheck(
        name="local_home",
        status="fail",
        summary=f"Craik home does not exist at {paths.home}.",
        action="Run craik setup or craik home init.",
    )


def _store_checks(paths: CraikPaths) -> list[DiagnosticCheck]:
    database_path = paths.state / DATABASE_NAME
    if not database_path.exists():
        return [
            DiagnosticCheck(
                name="local_store",
                status="fail",
                summary=f"Local store database is missing at {database_path}.",
                action="Run craik setup.",
            )
        ]
    store = LocalStore(database_path)
    try:
        version = store.migration_version()
    except LocalStoreError as error:
        return [
            DiagnosticCheck(
                name="local_store",
                status="fail",
                summary=f"Local store could not be inspected: {error}",
                action="Re-run setup or inspect the local SQLite store.",
            )
        ]
    finally:
        store.close()
    return [
        DiagnosticCheck(
            name="local_store",
            status="pass",
            summary=f"Local store is readable at migration {version}.",
        )
    ]


def _memory_backend_check(env: dict[str, str]) -> DiagnosticCheck:
    if env.get("CRAIK_STIGMEM_URL"):
        return DiagnosticCheck(
            name="memory_backend",
            status="pass",
            summary="Stigmem URL is configured. Run connect diagnostics for live compatibility.",
        )
    return DiagnosticCheck(
        name="memory_backend",
        status="warning",
        summary="Stigmem URL is not configured; local proposal memory remains available.",
        action="Set CRAIK_STIGMEM_URL and run craik connect stigmem when shared memory is needed.",
    )


def _gateway_checks(config: GatewayConfig | None) -> list[DiagnosticCheck]:
    if config is None:
        return [
            DiagnosticCheck(
                name="gateway_config",
                status="warning",
                summary="No gateway_default configuration is stored.",
                action="Run craik setup.",
            ),
            DiagnosticCheck(
                name="gateway_prerequisites",
                status="warning",
                summary="Gateway daemon prerequisites cannot be checked without config.",
                action="Run craik setup.",
            ),
            DiagnosticCheck(
                name="policy",
                status="warning",
                summary="Gateway policy readiness cannot be checked without config.",
                action="Persist a gateway config with a policy envelope before external ingress.",
            ),
        ]
    checks = [
        DiagnosticCheck(
            name="gateway_config",
            status="pass",
            summary=(
                f"Gateway config {config.id} is stored for "
                f"{config.bind_host}:{config.port}."
            ),
        )
    ]
    if config.mode == "daemon" and config.pid_file:
        checks.append(
            DiagnosticCheck(
                name="gateway_prerequisites",
                status="pass",
                summary="Daemon mode has a pid file configured.",
            )
        )
    else:
        checks.append(
            DiagnosticCheck(
                name="gateway_prerequisites",
                status="fail",
                summary="Daemon mode requires a pid file.",
                action="Re-run craik setup or update gateway configuration.",
            )
        )
    if config.enabled and not config.policy_envelope_id:
        checks.append(
            DiagnosticCheck(
                name="policy",
                status="warning",
                summary="Gateway is enabled without a policy envelope.",
                action="Attach a policy envelope before accepting external ingress.",
            )
        )
    else:
        checks.append(
            DiagnosticCheck(
                name="policy",
                status="pass",
                summary="Gateway policy boundary is inspectable.",
            )
        )
    return checks


def _open_existing_store(paths: CraikPaths) -> LocalStore | None:
    database_path = paths.state / DATABASE_NAME
    if not database_path.exists():
        return None
    return LocalStore(database_path)


def _overall_status(checks: list[DiagnosticCheck]) -> str:
    if any(check.status == "fail" for check in checks):
        return "fail"
    if any(check.status == "warning" for check in checks):
        return "warning"
    return "pass"
