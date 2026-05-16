# Handoffs

Handoffs are durable run summaries for the next agent or human reviewer.

A handoff records:

- task and project ids,
- the intent lock id,
- agent identity,
- run status,
- summary,
- completed actions,
- files and artifacts,
- commands and validation,
- assumptions,
- context debt,
- policy exceptions,
- receipts,
- memory proposals,
- and next steps.

Handoffs are not transcripts. They are concise continuity records that should let the next actor understand what happened, what was verified, what remains uncertain, and where to resume.

## Structured And Markdown Output

Craik persists handoffs as `craik.handoff` records in the local SQLite store.

Create a JSON handoff:

```sh
craik handoff create task_review_docs --summary "Updated docs." --test-run pytest
```

Show it as Markdown:

```sh
craik handoff show task_review_docs --markdown
```

The structured handoff is the durable source of truth. Markdown output is a readable rendering of the same record.

## Self-Audit

Every handoff includes a self-audit checklist. The checklist makes it explicit whether the run validated schema shape, reviewed redaction, reviewed receipts, reviewed assumptions, recorded validation, and disclosed policy exceptions.

Incomplete handoffs are valid, but they must make missing validation or unresolved context visible.
