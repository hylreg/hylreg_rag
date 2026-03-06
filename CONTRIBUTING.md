# Contributing Guide

Thanks for considering a contribution.

## Development Setup

1. Create and activate a virtual environment.
2. Install dependencies:
```bash
uv pip install -e ".[dev]"
```
3. Install git hooks:
```bash
pre-commit install
```
4. Copy environment template:
```bash
cp .env.example .env
```

## Local Checks

Run all checks before opening a PR:

```bash
make test
black --check .
flake8 src tests
mypy src
```

## Branching and PRs

1. Create a feature branch from `main`.
2. Keep changes focused and small.
3. Add or update tests for behavior changes.
4. Update docs (`README.md`, `USAGE.md`, changelog) when needed.
5. Open a PR using the template and ensure CI is green.

## Commit Messages

Use concise, imperative commits, for example:

- `feat(api): add upload size guard`
- `fix(core): handle empty vector index`
- `docs: clarify environment variables`

## Reporting Issues

Use the issue templates and include:

- Reproduction steps
- Expected vs actual behavior
- Environment details (OS, Python version, package versions)
