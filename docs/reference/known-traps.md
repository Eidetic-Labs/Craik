# Known Traps And Negative Knowledge

Known traps are evidence-backed pitfalls agents should avoid. Negative knowledge
records evidence-backed statements about what is not true or not available in a
scope.

`craik.known_trap` records the trap statement, avoidance guidance, evidence,
handoff links, optional expiry, and whether the trap is active, expired, or
contradicted.

`craik.negative_knowledge` records a bounded negative statement, its scope,
trust class, evidence, handoff links, contradictions, and optional expiry.

Use negative knowledge only when absence matters and there is evidence for it,
such as an inspected repository tree or a fresh tool attestation. Do not promote
unsupported guesses about absence into negative knowledge.

Active, unexpired known traps are surfaced in onboarding and case-file stale-risk
warnings so agents can avoid repeating known mistakes.
