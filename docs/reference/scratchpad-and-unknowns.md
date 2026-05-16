# Scratchpad And Unknowns

Scratchpad records are temporary working notes. They must expire and should not
be treated as durable context unless promoted through an explicit review path.

`craik.scratchpad_record` stores owner, note text, evidence links, status,
creation time, and expiry. Expired scratchpad records are filtered from active
runtime context.

Unknown records preserve explicit gaps instead of forcing agents to guess.
`craik.unknown_record` stores the question, owner, what is needed to resolve it,
next action, evidence, and resolution details when available.

Unresolved unknowns are surfaced in case-file stale risks and handoff context
debt so future agents see what remains unknown before continuing.
