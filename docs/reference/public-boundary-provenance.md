# Public Boundary And Provenance

Craik public docs must not expose private paths, raw credentials, internal-only
task labels, or local secret filenames. `craik.runtime.public_docs` provides the
machine-checkable MVP boundary.

## Classification

Work products are classified as:

- `public`: README, changelog, and Docusaurus docs;
- `internal`: source, tests, scripts, CI, and unclassified repository work;
- `private`: local state, secret paths, and user-specific runtime files.

## Hygiene

`scripts/check_public_docs_hygiene.py` scans public docs for obvious leaks. The
CI security gate runs it with release-readiness and policy tests.

## Provenance

Generated docs should carry evidence links back to source files, tests, or
commands that support the generated content. `generated_doc_provenance` creates
`craik.evidence_reference` records for those source links.

## Staleness

`stale_documentation_findings` compares generated docs against source mtimes and
returns stale-risk findings when a source is newer than the generated doc.

Repeated boundary findings should produce decision records for path redaction,
secret handling, or task naming.
