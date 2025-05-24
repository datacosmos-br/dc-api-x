# Contributing Guide

> *"Great software is the result of passionate contributors working together."*
> This guide outlines the contribution process for DCApiX, ensuring
> consistent quality across the integration ecosystem.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [10 - Development: Workflow](10-development-workflow.md) | **11 - Development: Contributing** | [12 - Development: Code Quality](12-development-code-quality.md) |

---

## 1. Contribution Process

The DCApiX contribution process follows these key steps:

1. **Fork → branch → PR** - Fork the repository, create a feature branch, submit a pull request
2. **Add or update unit tests** - Maintain test coverage ≥ 90%
3. **Update CHANGELOG.md** - Use *Keep a Changelog* style
4. **Run pre-commit checks** - Ensure `pre-commit run --all-files` passes locally
5. **Get reviews** - One keeper reviewer + one domain reviewer required

---

## 2. Coding Standards

DCApiX enforces rigorous coding standards to maintain quality:

* **Follow PEP 8** and our stricter rules (see [12 - Development: Code Quality](12-development-code-quality.md))
* **Add Google-style docstrings** to all public APIs
* **Adhere to wemake-python-styleguide** rules to minimize code complexity
* **Use underscore prefix** for unused arguments to avoid ARG002 lint errors
* **Break complex functions** into smaller, focused ones to keep cognitive complexity low
* **Add SPDX header + copyright** on every new file:

```python
# SPDX-License-Identifier: MIT
# © 2025 Datacosmos – Marlon Costa <marlon.costa@datacosmos.com.br>
```

---

## 3. Pull Request Process

Follow these steps when submitting a pull request:

1. **Ensure your branch is up-to-date** with `main`
2. **Fill out the PR template** completely, linking related issues
3. **Wait for CI to pass** before requesting review
4. **Address all review comments** promptly
5. **Merge after approval** - A maintainer will merge your PR once approved

---

## 4. Commit Message Format

DCApiX uses the Conventional Commits style:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types include: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.

Examples:

```
feat(auth): add support for OAuth2 authentication

Add OAuth2 authentication provider to support modern auth flows.
Includes refresh token handling and proper token expiration.

Fixes #123
```

```
fix(adapter): correct HTTP header handling in HTTPX adapter

The adapter was not properly passing custom headers to the HTTPX client.
This fix ensures all headers are correctly forwarded.
```

---

## 5. Development Workflow

Follow this workflow for efficient contribution:

1. **Create a topic branch** from `main`
2. **Install development dependencies**: `pip install -e ".[all,dev]"`
3. **Make your changes** and add appropriate tests
4. **Run tests locally**: `pytest -q --cov`
5. **Format code**: `make format`
6. **Run pre-commit checks**: `pre-commit run --all-files`

---

## 6. Architecture Decision Records

For significant architectural changes, create an ADR in `docs/adr/`:

1. **Copy the template** from `docs/adr/template.md`
2. **Number it sequentially**: `NNNN-short-title.md`
3. **Include key sections**: context, decision, consequences, and alternatives
4. **Reference the ADR** in your PR description

Example ADR filename: `0001-use-pluggy-for-plugin-system.md`

---

## 7. Documentation Contributions

Documentation is a key part of DCApiX:

* **Keep documentation up-to-date** with code changes
* **Follow the documentation style guide** for consistency
* **Add examples** to illustrate complex concepts
* **Update cross-references** between documents

---

## Related Documentation

* [10 - Development: Workflow](10-development-workflow.md) - Development workflow guide
* [12 - Development: Code Quality](12-development-code-quality.md) - Code quality standards
* [13 - Development: Plugin System](13-development-plugin-system.md) - Plugin development guide
* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
