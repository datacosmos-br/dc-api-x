# Repository & Source Layout

dc-api-x follows the **src-layout** pattern recommended by PyPA.  
That means *all* importable code lives under `src/`, ensuring unit tests run
against the *installed wheel* instead of the checkout path—so packaging issues
surface immediately.

```text
.
├── docs/                  # Project documentation (this folder)
│   ├── 00-overview.md
│   ├── 01-installation.md
│   └── … (architecture, contributing, …)
│
├── examples/              # Copy-runnable scripts and notebooks
│   ├── rest_api_client.py
│   ├── github_api_client.py
│   └── schema_extraction.py
│
├── src/                   # **ONLY** importable code lives here
│   └── dc_api_x/
│       ├── __init__.py    # Re-exports + bootstrap
│       ├── client.py      # ApiClient façade (sync + async)
│       ├── cli.py         # Typer-based `dcapix` CLI
│       ├── config.py      # Profile/ENV config loader
│       ├── exceptions.py  # Canonical error hierarchy
│       ├── models.py      # Core pydantic types
│       │
│       ├── ext/           # Public extension interfaces
│       │   ├── adapters.py
│       │   ├── auth.py
│       │   ├── hooks.py
│       │   └── providers.py
│       │
│       ├── hookspecs/     # pluggy hook declarations
│       │   └── hookspecs.py
│       │
│       ├── pagination/    # Generic paginator helpers
│       ├── schema/        # JSON-Schema & OpenAPI helpers
│       ├── entity/        # Dynamic Entity API (CRUD wrappers)
│       ├── utils/         # Reusable helpers (logging, validation…)
│       ├── plugin_manager.py
│       └── plugins/       # Thin registry for built-in plugins
│           ├── base.py
│           └── registry.py
│
├── tests/                 # Pytest suite
│   ├── unit/              # Fast, isolated tests
│   ├── integration/       # Require network / OCI sandbox
│   ├── fixtures/          # Reusable JSON & LDIF blobs
│   └── conftest.py        # Pytest plugins + factories
│
├── Makefile               # One-liner dev tasks (`make test`, `make lint`)
├── pyproject.toml         # Poetry, build-system, linters, extras
├── poetry.lock            # Locked dependency graph
├── README.md              # Front-page on GitHub / PyPI
└── LICENSE                # MIT (SPDX)
```

---

## 1  Directory Cheat-Sheet

| Path             | What belongs here                                                                                                           |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `docs/`          | Every `.md` file included in the static site or MkDocs build. One topic per file.                                           |
| `examples/`      | Self-contained scripts that run with **only** the public API. Keep them under 100 LOC.                                      |
| `src/dc_api_x/`  | Package code. *No* tests, *no* docs, *no* data dumps.                                                                       |
| `tests/`         | Pytest modules mirroring the `src/` tree. Fast unit tests inside `tests/unit`, slower network tests in `tests/integration`. |
| `Makefile`       | Shortcuts: `format`, `lint`, `test`, `docs`, `clean`, `publish`.                                                            |
| `pyproject.toml` | Single source of truth for Poetry, extras, lint config, ruff/mypy settings and entry-points.                                |

> **Convention:**
> If a file could be imported at runtime, it lives in `src/`.
> Everything else (docs, tests, CI helpers, artefacts) lives *outside* `src/`.

---

## 2  Adding a New Sub-package

1. **Create folder** inside `src/dc_api_x/` (e.g. `dataclasses/`).
2. Add `__init__.py` with explicit `__all__`.
3. Update *public re-exports* **only** if the module is part of the public API.
4. Write unit tests under `tests/unit/dataclasses/test_*.py`.
5. Add a stub page in `docs/` if user-facing.
6. Touch `CHANGELOG.md`.
7. Run `make lint test docs`.

---

## 3  What the Makefile Does

| Target             | Command                          | Purpose                         |
| ------------------ | -------------------------------- | ------------------------------- |
| `make install-dev` | `pip install -e .[all,dev]`      | Full dev environment.           |
| `make lint`        | `ruff + mypy + bandit`           | Static analysis gate.           |
| `make test`        | `pytest -q --cov`                | Unit + integration tests.       |
| `make format`      | `black . && isort .`             | Opinionated formatting.         |
| `make docs`        | `mkdocs build` or `sphinx-build` | Generates HTML docs to `site/`. |
| `make build`       | `poetry build`                   | Creates wheel + sdist.          |
| `make publish`     | `poetry publish -r datacosmos`   | Pushes to internal PyPI.        |

---

## 4  Tooling Overview

| Tool              | Config file                   | Enforced in CI |
| ----------------- | ----------------------------- | -------------- |
| **Poetry**        | `pyproject.toml`              | ✅              |
| **black**         | `pyproject.toml [tool.black]` | ✅              |
| **isort**         | `pyproject.toml [tool.isort]` | ✅              |
| **ruff**          | `pyproject.toml [tool.ruff]`  | ✅              |
| **mypy**          | `pyproject.toml [tool.mypy]`  | ✅              |
| **pytest**        | `pytest.ini`                  | ✅              |
| **Sphinx/MkDocs** | `docs/` + `Makefile`          | optional       |

All lint/test steps run in GitHub Actions across *Python 3.10 · 3.11 · 3.12*.

---

## 5  FAQ

| Question                                    | Answer                                                                                    |
| ------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **Why src-layout instead of flat package?** | Prevents accidental imports from the local checkout; mirrors how users install via wheel. |
| **Can I place scripts in `src/`?**          | No—scripts belong in `examples/` or `bin/`.                                               |
| **Where do generated artefacts go?**        | `dist/` for wheels, `site/` for docs. Both are ignored by Git.                            |

---

*Enjoy a clean, predictable project tree—future contributors will thank you!* 🚀
