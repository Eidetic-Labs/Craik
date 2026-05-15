# Project Registry

Craik projects are local Git repositories registered into the local store.

Register a project:

```sh
craik project add /path/to/repo
```

Register with explicit documentation and immutable paths:

```sh
craik project add /path/to/repo \
  --name stigmem \
  --docs-path README.md \
  --docs-path docs/ \
  --immutable-path docs/adr/
```

List registered projects:

```sh
craik project list
```

Show a project by id or name:

```sh
craik project show stigmem
```

Project registration writes only to Craik local state under `~/.craik` or `$CRAIK_HOME`. It does not create project-local `.craik/` metadata inside the repository.

