# Limitations

Craik is pre-0.1.0.

Current limitations:

- The package and CLI scaffold exist, but end-to-end runtime workflows are not implemented yet.
- The local SQLite store, project registry, policy profiles, capability grant checks, central redaction utility, and receipt store exist, but no full policy enforcement engine, memory backend, runner adapter, automatic receipt-producing workflow, or handoff writer is available yet.
- The CLI does not request tool authority or write runtime state.
- Stigmem integration is planned but not implemented in this package scaffold.
