# Maintenance Guide

## Release Process

1. Ensure `main` is green in CI.
2. Update `CHANGELOG.md` under `Unreleased`.
3. Create a version tag:
```bash
git tag v0.1.1
git push origin v0.1.1
```
4. `release.yml` builds artifacts and creates a GitHub release.
5. If `PYPI_API_TOKEN` is configured, package is also published to PyPI.

## Dependency Management

- Dependabot opens weekly updates for pip and GitHub Actions.
- Review dependency PRs with:
```bash
make check
```
- Security scan runs via `security.yml` and `pip-audit`.

## Branch Protection (Recommended)

Enable on `main`:

- Require PR reviews (at least 1)
- Require status checks: CI + Security
- Require conversation resolution
- Restrict direct pushes

## Ownership

- Update `.github/CODEOWNERS` with real teams/users.
- Ensure at least two maintainers can merge and release.

