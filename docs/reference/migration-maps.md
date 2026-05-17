# Migration Maps

Migration maps describe how source fields become Craik fields for memory, skill,
and config imports.

`MigrationFieldMap` records:

- source field;
- target Craik field;
- support level: `supported`, `partial`, or `unsupported`;
- transformation notes;
- redaction requirement;
- unsupported reason.

`MigrationMap` records:

- map id;
- surface: `memory`, `skill`, or `config`;
- source name;
- field maps;
- compatibility notes;
- policy envelope id;
- evidence ids;
- receipt ids.

## Usage

Importers should use migration maps during dry runs before mutating state.
Supported fields can be transformed into Craik records. Partial fields require
operator review. Unsupported fields must remain out of imported records and
should produce dry-run warnings or errors.

Secrets, credentials, private payloads, and local-only paths should be marked
unsupported or redacted rather than copied.

Migration maps preserve policy, evidence, and receipt links so future importers
can explain why a field was transformed, skipped, or blocked.
