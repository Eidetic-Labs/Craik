# Plugin Probation

Plugin probation records keep new or changed plugins out of durable trust until
review criteria are satisfied.

The `craik.plugin_probation` contract links a plugin descriptor to:

- policy envelope;
- review criteria;
- compatibility checks;
- evidence and receipt records;
- promotion, rejection, or expiration decisions;
- whether durable trust was granted.

Probation records start with `status: probationary` and
`durable_trust_granted: false`. Probationary records cannot include a decision or
grant durable trust.

## Review States

`promoted` records require a promote decision, passing required criteria, and
compatibility checks. Promotion does not have to grant durable trust; the field
defaults to false so callers make durable trust explicit.

`rejected` records require a reject decision.

`expired` records require an expire decision and `expires_at`.

These states make plugin review auditable without mixing descriptor metadata
with runtime authority or policy grants.
