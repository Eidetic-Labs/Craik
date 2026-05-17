# Adjacent-Tool Migration Assessment

Adjacent-tool migration assessments describe how concepts from nearby tools map
into Craik before an importer is built.

`AdjacentToolMapping` records:

- source concept;
- target Craik concept: `project`, `task`, `memory`, `skill`, `config`, or
  `receipt`;
- support level: `supported`, `partial`, or `unsupported`;
- notes;
- required controls;
- unsupported fields.

`AdjacentToolMigrationAssessment` records:

- assessment id;
- tool name;
- overall support level;
- mappings;
- security notes;
- redaction requirement;
- policy envelope id;
- evidence ids;
- receipt ids.

## Compatibility

Supported mappings can be converted without losing Craik's policy, evidence,
receipt, and redaction model.

Partial mappings need operator review. Unsupported fields must be named so a
dry run can warn without mutating state.

Unsupported mappings should not be imported. Secrets and credentials should be
reconfigured by an operator instead of copied from the source tool.

## Boundary

An assessment is not an import. It is an evidence-backed compatibility record
that can later feed import dry-run reports, migration maps, and bridge
decisions.
