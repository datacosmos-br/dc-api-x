# Contributing Guide

1. **Fork → branch → PR**  
2. Add or update **unit tests**; keep coverage ≥ 90 %.  
3. Update `CHANGELOG.md` using *Keep a Changelog* style.  
4. Ensure `pre-commit run --all-files` passes locally.  
5. One κeeper reviewer + one domain reviewer required.

## Coding Standards

* Follow PEP 8 & our stricter rules (see *Code-Quality* doc).  
* Public APIs **must** have Google-style docstrings.  
* Adhere to wemake-python-styleguide rules to minimize code complexity.
* Use underscore prefix for unused arguments to avoid ARG002 lint errors.
* Break complex functions into smaller, focused ones to keep cognitive complexity low.
* Add SPDX header + copyright on every new file:

```python
# SPDX-License-Identifier: MIT
# © 2025 Datacosmos – Marlon Costa <marlon.costa@datacosmos.com.br>
```

## Pull Request Process

1. Ensure your branch is up-to-date with `main`.
2. Fill out the PR template completely, linking related issues.
3. Wait for CI to pass before requesting review.
4. Address all review comments promptly.
5. Once approved, a maintainer will merge your PR.

## Commit Message Format

Use the Conventional Commits style:

```html
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.

## Development Workflow

1. Create a topic branch from `main`.
2. Install development dependencies: `pip install -e .[all,dev]`.
3. Make your changes and add tests.
4. Run tests locally: `pytest -q --cov`.
5. Format code: `make format`.
6. Run pre-commit checks: `pre-commit run --all-files`.

## Architecture Decision Records

For significant architectural changes, create an ADR in `docs/adr/`:

1. Copy the template from `docs/adr/template.md`.
2. Number it sequentially: `NNNN-short-title.md`.
3. Include context, decision, consequences, and alternatives.
4. Reference the ADR in your PR description.
