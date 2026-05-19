# Development Checks

Craik requires Python 3.12 or 3.13. Python 3.14 is not supported yet because
the current Pydantic runtime dependency does not publish compatible wheels.

Use `uv` for reproducible local validation:

```sh
uv run --python 3.12 --extra dev pytest
uv run --python 3.12 --extra dev ruff check .
uv run --python 3.12 --extra dev mypy
uv run --python 3.12 --extra dev craik policy test
```

The same checks run in CI for pull requests and pushes to `main`.
