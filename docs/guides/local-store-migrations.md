# Local Store Migrations

Craik stores local runtime state in SQLite at `state/craik.sqlite3`.
Migrations are forward-only and run during `LocalStore.initialize()`.

## Version Tracking

Craik records the current migration in two places:

- SQLite `PRAGMA user_version`;
- the `migrations` table, with one row per applied migration.

Migration `2` also creates `local_store_metadata`, which records the current
store schema version and the contract registry count visible to the installed
Craik build.

## Compatibility Fixtures

Migration compatibility tests load prior schema fixtures from
`tests/fixtures/local_store/`. The v1 fixture describes the first records-based
store layout and is migrated to the current schema during tests. This keeps old
local stores on an explicit compatibility path instead of depending only on
fresh database initialization.

## Failure Handling

Failed migrations raise a local store migration error with recovery guidance.
Operators should:

1. Back up `state/craik.sqlite3`.
2. Keep the original file unchanged.
3. Run `craik doctor` for diagnostics.
4. If the database version is newer than the installed Craik build supports,
   upgrade Craik before opening the store.
5. If a migration failed partway through, restore the backup or copy the
   database aside before retrying.

Craik does not silently recreate unreadable local stores. Recreating local state
would discard receipts, handoffs, memory proposals, case files, and task runs
that may be needed for audit or recovery.
