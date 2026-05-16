# Plugin Capability Grants

Plugin capability grants scope runtime authority to one plugin descriptor.

The `craik.plugin_capability_grant` contract records:

- task and plugin descriptor;
- policy envelope;
- capability name;
- target paths and exclusions;
- allowed operations;
- grant status;
- approval requirement and approver;
- expiry;
- evidence and receipt links.

Grant operations should stay least-privilege. A plugin that only needs read
access should receive only `read`, even if the underlying policy profile could
allow broader authority.

## States

`allowed` grants require expiry. If approval is required, `approved_by` is also
required.

`denied` grants must not include `approved_by`.

`expired` grants require `expires_at`.

`approval_required` grants represent pending authority. They must set
`approval_required` and must not include `approved_by` until a human or policy
decision approves the grant.
