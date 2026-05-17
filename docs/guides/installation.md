# Installation

Craik is not published to PyPI yet. During `0.x.0` MVP development, install it
from a local checkout:

```sh
python3.12 -m pip install -e ".[dev]"
```

After installation, verify the CLI is available:

```sh
craik --version
```

Craik requires Python 3.12 or newer.

For reproducible source-tree commands, use `uv`:

```sh
uv run --python 3.12 --extra dev craik --version
```

Runtime state is stored under `~/.craik` unless `CRAIK_HOME` is set.
