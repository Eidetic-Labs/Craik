# Context Debt

Context debt records preserve known gaps in the context an agent used. They make
omissions explicit so future agents can decide whether to continue, refresh, or
stop for more information.

`craik.context_debt_record` can represent:

- omitted documentation,
- documentation excluded by discovery rules,
- stale instruction constraints,
- unresolved assumptions,
- missing external state such as GitHub,
- missing memory facts,
- active instruction constraints carried forward,
- missing case files,
- or another explicit context gap.

Open and carried-forward records must include `next_action`. Resolved records
must include `resolved_at`.

Handoffs continue to expose a deterministic `context_debt` summary list for
runner readability. The structured records are persisted separately so callers
can track owner, source links, next action, carry-forward state, and resolution.
