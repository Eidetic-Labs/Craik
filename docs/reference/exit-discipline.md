# Context Requests And Exit Discipline

Context requests are structured asks for information needed before work can
continue safely. They can link to handoffs, recovery sessions, and unresolved
unknowns.

`craik.context_request` records requester, kind, status, question, why the
context is needed, and fulfillment details when available.

`craik.exit_discipline_check` records whether an agent exit included:

- validation,
- a handoff,
- residual risk state,
- next steps,
- context request links,
- and unresolved unknown links.

Complete exits require every checklist field and no blockers. Blocked exits must
explain blocking reasons so the next agent can recover without guessing.
