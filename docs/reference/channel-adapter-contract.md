# Channel Adapter Contract

`craik.channel_adapter_contract` defines the boundary for external operator
ingress through always-on gateway channels.

The contract is descriptive. It lets Craik validate and inspect channel adapter
identity, payload shape, capabilities, receipts, and trust boundaries before a
specific adapter is wired into the gateway.

## Identity

Channel adapter identity includes:

- stable adapter id;
- channel kind, such as `messaging`, `webhook`, `scheduler`, `voice`, or
  `custom`;
- human-readable name;
- adapter version;
- optional external service name.

Identity is not authorization. It only identifies the adapter implementation and
channel family.

## Capabilities

Each adapter declares one or more capability names with:

- direction: `inbound`, `outbound`, or `bidirectional`;
- description;
- whether a grant is required;
- whether a receipt is required.

Channel capabilities are still governed by policy envelopes and explicit grants.
Adapters do not receive ambient authority from being installed or configured.

## Inbound Events

Inbound event shapes must include:

- `event_id`;
- `channel`;
- `received_at`;
- `sender`.

Adapters may include additional normalized fields such as `text`, `thread_id`,
or channel-specific metadata. Sensitive payload fields should be listed in
`redacted_fields`.

## Outbound Responses

Outbound response shapes must include:

- `status`;
- `summary`.

Adapters may include delivery metadata, response ids, text bodies, receipt ids,
or channel-specific fields. Provider details remain nested under metadata rather
than expanding the core contract into a channel matrix.

## Receipts

Channel adapter contracts require `craik.capability_receipt` receipts. Receipt
capabilities must be declared by the adapter contract, so inbound and outbound
channel activity stays auditable under the same policy model as runner and tool
actions.

## Trust Boundaries

Channel adapter contracts require:

- policy envelopes;
- allowlist enforcement;
- inbound identity handling;
- secrets outside contract and config payloads.

Future channel adapters can add delivery-specific behavior, but they must keep
authorization, identity pairing, redaction, and receipt emission visible at this
contract boundary.
