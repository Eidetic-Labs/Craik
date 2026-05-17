# Secret Migration Policy

Craik migration workflows must never copy secret values from an adjacent tool,
workflow engine, or configuration source into the target runtime. Secret-bearing
fields are handled through one of four policy outcomes:

- `redact`: replace the source value with a redaction marker in reports and
  receipts.
- `reference`: preserve only a non-secret reference identifier, such as a vault
  key name.
- `reconfigure`: require the operator to recreate or bind the secret in the
  target environment.
- `block`: stop the field or record from migrating until an explicit policy
  decision exists.

Unknown fields that contain secret material are blocked by default. A migration
policy cannot authorize secret value copying, and secret decisions require
receipts so reviewers can see what was redacted, referenced, or deferred to
operator setup.

## Runtime Contract

`SecretMigrationPolicy` records the source, policy envelope, evidence, receipts,
and field-level rules. Each `SecretMigrationPolicyRule` defines the source field,
safe handling mode, reason, dry-run warning, and whether operator action is
required.

`evaluate_secret_migration` returns a `SecretMigrationDecision` for a source
field:

- non-secret fields are allowed without secret receipts;
- matching secret rules return `redacted`, `referenced`,
  `operator_reconfiguration_required`, or `blocked`;
- unmapped secret fields return `blocked`;
- every secret decision sets `copied_secret_value` to `false`.

## Dry-Run Behavior

Import dry-run reports should include warnings from the secret migration policy.
Warnings must describe the safe handling outcome without exposing the source
value. Reports may name fields, schemas, and reference identifiers, but public
docs and public receipts must not include local filesystem paths, credentials,
private task names, or copied secret bytes.

## Receipts

Secret migration receipts should record:

- the policy envelope that governed the decision;
- evidence used to classify the field as secret-bearing;
- the safe handling outcome;
- required operator action, when applicable;
- confirmation that no secret value was copied.
