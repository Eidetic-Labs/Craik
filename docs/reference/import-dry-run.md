# Import Dry-Run Reports

Import dry-run reports show what a migration import would do without mutating
Craik state.

`ImportCandidateRecord` records:

- source id;
- source type;
- redacted summary;
- redaction status.

`ImportMappedRecord` records:

- source id;
- target schema;
- target id;
- status: `mapped`, `warning`, `error`, or `unsupported`;
- warnings;
- errors.

`ImportDryRunReport` records:

- source name and kind;
- candidate records;
- mapped records;
- warnings;
- errors;
- `mutated_state: false`;
- redaction status;
- policy envelope id;
- evidence ids;
- receipt ids.

## Boundary

Dry runs do not write tasks, memory, skills, config, receipts, or artifacts.
They are compatibility reports for operator review.

Warnings indicate records that need review before import. Errors and
unsupported mappings prevent import until the source data or migration map is
changed.

Dry-run reports must preserve policy, evidence, and receipt links so migration
decisions remain auditable.
