# Limitations

Craik is pre-0.1.0.

Current limitations:

- The package and CLI scaffold exist, but end-to-end runtime workflows are not implemented yet.
- The local SQLite store, project registry, task creation, intent locks, local case file assembler, read-only GitHub context, work graph export, handoff writer, local contradiction reports, local memory proposal backend, minimum Stigmem backend compatibility, policy profiles, capability grant checks, central redaction utility, and receipt store exist, but no full policy enforcement engine, runner adapter, or automatic receipt-producing workflow is available yet.
- Local memory search returns approved local proposals only; direct durable writes remain unavailable without a future memory-write grant path.
- Stigmem direct writes require explicit `memory.write` grants; proposal review remains the default path.
- Memory diffs and impact previews currently derive from local proposal state and approved local facts; runner-normalized fact reads, direct Stigmem write receipts, and write-failure ingestion are not wired into full workflows yet.
- Handoffs currently derive context debt from local case files only; they do not yet include runner result normalization or remote artifact upload.
- Agent onboarding summarizes local state and configured Stigmem environment presence, but it does not perform live Stigmem backend discovery.
- Case files currently load local project/task/repo/docs context and read-only GitHub state when configured; Stigmem facts, recent handoffs, and local contradiction report loading are not wired into case assembly yet.
- The Stigmem documentation demo creates local proposed updates and artifacts; it does not edit documentation files or directly write Stigmem facts by default.
- Policy tests cover current policy primitives and keep runner grant boundaries visible, but runner adapters are not implemented yet.
- Runner capability matrices and trust profiles are available for preview runner ids, but prompt compilation and runtime runner selection are not wired to them yet.
- Prompt compilation produces deterministic runner-ready prompts, but it does not invoke live runners or enforce grants at execution time yet.
- The CLI does not request tool authority or write runtime state.
- Stigmem integration is limited to compatibility detection, fact query/get/provenance mapping, and policy-gated direct fact writes.
