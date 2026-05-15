# Configuring Craik Home

Craik stores local runtime state under:

```text
~/.craik/
```

Set `CRAIK_HOME` to use a different location:

```sh
CRAIK_HOME=/custom/path craik home show
```

Inspect resolved paths without creating directories:

```sh
craik home show
```

Create the local state layout:

```sh
craik home init
```

`craik home show` is read-only. It does not create `~/.craik` or project-local metadata.

