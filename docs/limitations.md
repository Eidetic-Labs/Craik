# Limitations

Craik is pre-0.1.0.

Current limitations:

- The package and CLI scaffold exist, but end-to-end runtime workflows are not implemented yet.
- The local SQLite store, project registry, task creation, intent locks, local case file assembler, handoff writer, policy profiles, capability grant checks, central redaction utility, and receipt store exist, but no full policy enforcement engine, memory backend, runner adapter, or automatic receipt-producing workflow is available yet.
- Handoffs currently derive context debt from local case files only; they do not yet include runner result normalization or remote artifact upload.
- Case files currently load local project/task/repo/docs context only; Stigmem facts, GitHub state, recent handoffs, and contradiction reports are not loaded yet.
- The CLI does not request tool authority or write runtime state.
- Stigmem integration is planned but not implemented in this package scaffold.
