# Installation

Install Craik from PyPI:

```sh
python3.12 -m pip install craik
```

Or install it with `pipx` if you want an isolated CLI:

```sh
pipx install --python python3.12 craik
```

For contributor development, install it from a local checkout:

```sh
python3.12 -m pip install -e ".[dev]"
```

After installation, verify the CLI is available:

```sh
craik --version
```

Craik requires Python 3.12 or 3.13. Python 3.14 is not supported yet because
the current Pydantic runtime dependency does not publish compatible wheels.

For reproducible source-tree commands, use `uv`:

```sh
uv run --python 3.12 --extra dev craik --version
```

Runtime state is stored under `~/.craik` unless `CRAIK_HOME` is set.

## First-Time Configuration

Initialize local state before running project workflows:

```sh
craik home init
```

Fixture-backed provider execution works without credentials. For live provider
calls, authenticate the operator and add a credential profile:

```sh
craik login
craik auth add anthropic:work --kind=api-key --env-var=ANTHROPIC_API_KEY
```

See [Authentication and Credentials](authentication.md) for OIDC login,
credential profiles, approval flow, and workload-identity setup.
