# Channel Identity Pairing

`craik.channel_identity_pairing` records the relationship between an external
channel account and a Craik subject.

Pairing state is separate from channel adapter identity. A messaging adapter can
normalize inbound events, but an external sender cannot authorize privileged
ingress until a pairing record explicitly links that sender to a Craik subject,
policy envelope, and audit trail.

## States

### Unpaired

An unpaired record captures the observed external account only:

- channel kind;
- external account id;
- optional service name;
- optional display name;
- optional metadata.

Unpaired records must not carry a subject, policy envelope, pairing audit fields,
or revocation fields. They do not allow privileged ingress.

### Paired

A paired record must include:

- Craik subject;
- policy envelope id;
- pairing timestamp;
- actor that approved the pairing;
- at least one audit id.

Paired identities can authorize privileged ingress only through the linked
policy envelope and only when later allowlist and capability checks pass.

### Revoked

A revoked record preserves the original subject and pairing audit fields, then
adds:

- revocation timestamp;
- actor that revoked the pairing;
- revocation reason;
- audit id for the revocation.

Revoked identities never allow privileged ingress.

## Authority Limits

Identity pairing does not grant broad channel access. It only establishes who an
external account maps to. Gateway policy, channel allowlists, capability grants,
redaction, and receipts still decide what can happen after an inbound event is
normalized.
