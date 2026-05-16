# Channel Allowlists

`craik.channel_allowlist` controls which normalized inbound channel events may
continue past the gateway ingress boundary.

Allowlists are deny-by-default. A channel event is allowed only when it matches
an enabled rule for the configured channel. Denied events produce explicit
decision reasons that can be recorded in redacted capability receipts.

## Rule Selectors

Allowlist rules can match:

- channel kind;
- provider or fixture service name;
- external sender ids;
- workspace ids;
- thread ids;
- string metadata keys.

Rules require at least one selector. Broad, selector-free allow rules are
rejected.

## Decisions

The evaluator returns an inspectable decision with:

- allowed or denied status;
- reason;
- matched rule id when allowed;
- event id;
- channel;
- sender external id.

Events from the wrong channel are denied before rule matching. Events with no
matching enabled rule are denied with `no enabled allowlist rule matched`.

## Denial Receipts

Denied inbound events can emit a `craik.capability_receipt` with the
`channel.ingress.denied` capability. Receipt metadata preserves the allowlist id,
event id, channel, sender external id, policy envelope id, and redaction fields
without storing message text.

## Configuration Limits

Channel allowlists do not pair identities, grant tool authority, or bypass
policy envelopes. They only decide whether a normalized external event can
continue to later gateway stages.

See [Channel Policy Envelopes](channel-policy-envelopes.md) for the scoped
policy selected after pairing and allowlist checks pass.
