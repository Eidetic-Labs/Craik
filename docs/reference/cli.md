# CLI Reference

Craik exposes the `craik` command.

## `craik --version`

Print the installed Craik package version.

## `craik version`

Print the installed Craik package version.

## `craik schema list`

List registered Craik runtime contract schemas.

## `craik schema show <name>`

Print the JSON Schema for a registered runtime contract.

## `craik home show`

Print resolved Craik local state paths without creating directories.

## `craik home init`

Create Craik's local state directories.

## `craik project add <path>`

Register a Git repository in the local project registry.

Options:

- `--name <name>`: project name; defaults to the repository directory name.
- `--docs-path <path>`: documentation path to include; may be repeated.
- `--immutable-path <path>`: immutable path to include; may be repeated.

## `craik project list`

Print registered projects as JSON.

## `craik project show <id-or-name>`

Print one registered project as JSON.

Additional commands will be documented as they are implemented.
