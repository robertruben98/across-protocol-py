# Contributing

Thanks for your interest in improving `across-protocol-py`.

## Development setup

```bash
git clone https://github.com/robertruben98/across-protocol-py.git
cd across-protocol-py
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks

All of these must pass before a PR is merged (CI enforces them):

```bash
ruff check .        # lint + import order
mypy src            # strict type checking
pytest -q           # unit tests (respx-mocked, no network)
```

The live integration test hits the real Across API and is skipped by default.
Run it explicitly when you want to verify against production:

```bash
pytest -m integration
```

## Conventions

- This library targets **Python 3.9+**. Do not use PEP 604 `X | None` syntax in
  runtime-evaluated annotations (pydantic models, function signatures);
  use `typing.Optional` / `typing.Union` instead. Bare `list[...]` / `dict[...]`
  generics are fine thanks to `from __future__ import annotations`.
- Add tests first (TDD). Cover new behavior and edge cases.
- Public methods get Google-style docstrings (Args / Returns / Raises).
- Model fields get a `Field(description=...)`.

## Releasing

Releases are published to PyPI automatically via Trusted Publishing when a
GitHub Release is published. Bump the version in `pyproject.toml` and
`src/across_protocol/__init__.py`, update `CHANGELOG.md`, then tag the release.
