# Channel Policy Envelopes

Channel ingress uses normal `craik.policy_envelope` records, but the selected
envelope is narrower than local operator authority.

`craik.runtime.channels.policy` binds a normalized inbound event to a channel
policy only when:

- the external sender has a paired channel identity;
- the allowlist decision is allowed;
- the policy remains fail-closed;
- receipts and redaction are required.

## Default Channel Authority

The default channel policy allows:

- `channel.message.receive`;
- `channel.message.respond`;
- `receipt.write`.

It denies local operator capabilities such as repository writes, immutable path
writes, shell execution, memory writes, GitHub writes, and gateway
administration.

## Denial Handling

Unpaired identities and allowlist rejections do not produce a policy envelope.
Requested capabilities outside the channel policy can emit redacted
`craik.capability_receipt` records with status `denied`.

Denial receipts preserve:

- policy envelope id when one was selected;
- event id;
- requested capability;
- channel;
- redaction fields.

Message text is not stored in policy denial receipt metadata.

## Boundary

Channel policy envelopes are ingress-scoped. They do not expand local operator
authority, bypass allowlists, pair external identities, or grant tool access by
themselves.
