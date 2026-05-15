# Development Checks

Craik requires Python 3.12 or newer.

Use `uv` for reproducible local validation:

```sh
uv run --python 3.12 --extra dev pytest
uv run --python 3.12 --extra dev ruff check .
uv run --python 3.12 --extra dev mypy
```

The same checks run in CI for pull requests and pushes to `main`.

