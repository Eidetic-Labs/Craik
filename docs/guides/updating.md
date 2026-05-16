# Updating Craik

`craik update` prints safe update guidance. It does not modify the installed
package, rewrite source checkouts, fetch remote release metadata, or migrate
local state.

```sh
craik update
```

The output includes:

- installed version;
- supported Python range;
- local store migration compatibility;
- contract compatibility;
- manual update steps;
- boundaries for what Craik will not do automatically.

## Recommended Flow

1. Review release notes and migration notes.
2. Run `craik doctor`.
3. Update Craik with the package manager or source checkout that installed it.
4. Run `craik doctor` again.
5. Run project validation before starting the gateway.

Future migration commands may add explicit local-state migrations, but update
guidance remains non-mutating by default.
