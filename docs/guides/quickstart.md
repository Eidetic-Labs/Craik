# Quickstart

Craik v0.1.0 is a CLI-first durable runtime for local project state, case files,
policy checks, receipts, handoffs, memory proposals, and the first Stigmem demo.

## Install

From a local checkout:

```sh
python3.12 -m pip install -e ".[dev]"
craik --version
```

For source-tree development with `uv`, prefix commands with:

```sh
uv run --python 3.12 --extra dev
```

## Create Local State

```sh
export CRAIK_HOME=/tmp/craik-quickstart
craik home init
```

## Register A Project

Run this inside or next to a Git repository:

```sh
craik project add . --name Example
```

Craik detects conventional docs paths such as `README.md`, `docs/`, and
immutable ADR paths such as `docs/adr/`.

## Create A Task

```sh
craik task create \
  --project Example \
  --title "Review docs" \
  --objective "Review documentation against implementation state." \
  --mode review \
  --out-of-scope "ADR edits"
```

The command creates both a task request and an intent lock.

## Build A Case File

```sh
craik case build task_review_docs --no-github
craik case show task_review_docs
```

Case files include project state, docs, immutable paths, assumptions, stale-risk
warnings, evidence, and a verification plan.

## Run Policy Tests

```sh
craik policy test
```

The policy gate verifies strict defaults, immutable path behavior, memory
proposal defaults, fail-open receipts, automation fail-closed behavior, and
redaction.

## Create A Handoff

```sh
craik handoff create task_review_docs \
  --summary "Reviewed docs and recorded current state." \
  --test-run "craik policy test" \
  --next-step "Review memory proposals."
```

## Run The Stigmem Demo

From a Stigmem checkout:

```sh
craik demo stigmem-docs --repo-path . --no-github
```

The demo creates local project, task, case-file, contradiction, memory proposal,
receipt, handoff, and work-graph artifacts without editing files or directly
writing Stigmem facts.
