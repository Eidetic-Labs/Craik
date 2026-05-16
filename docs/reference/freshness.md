# Tool Attestations And Freshness

Tool attestations record observed command or tool results with a trust boundary.
Freshness probes track when knowledge should be considered fresh, expiring,
expired, or missing.

`craik.tool_result_attestation` preserves:

- tool name and identity,
- command when available,
- observed output summary,
- trust class,
- evidence or receipt links,
- capture time,
- and optional expiry.

`craik.knowledge_freshness_probe` links a target such as GitHub state,
documentation, memory facts, tool results, external state, or instruction
sources to freshness status and stale-risk warning text.

Freshness probes are not proof that a claim is true. They only record whether
the expected source was observed recently enough for the caller's freshness
policy. Expiring, expired, and missing probes should be surfaced as stale-risk
warnings before a handoff or memory promotion relies on that knowledge.
