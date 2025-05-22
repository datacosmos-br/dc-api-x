# dc-api-x · Data Client API Extensions 🚀
>
> **The Datacosmos integration framework** – one import, one client, every protocol.

| &nbsp; | Highlight |
|-------|-----------|
| 🔗 **Unified access** | Single `ApiClient` façade, plug-in adapters (HTTP, Oracle, LDAP …) |
| 🛡️ **Type-safe** | `pydantic.BaseModel` everywhere, `mypy --strict` green |
| 🧩 **Drop-in plugins** | `pluggy` entry-points → add connectors without touching the core |
| 📈 **Observability** | Structured JSON/Rich logs, OpenTelemetry spans, Prom-ready metrics |
| 🏢 **Enterprise-grade** | PEP 8, `ruff`, `bandit`, ≥ 90 % coverage, ADR workflow |
| 📜 **MIT & SemVer** | SPDX headers, changelog gated |

**PyPI:** `dc-api-x`   **Import:** `import dc_api_x as apix`

```python
import dc_api_x as apix
```

---

## 📚 Documentation (Map)

| # | Document                                                | Purpose                                      |
| - | ------------------------------------------------------- | -------------------------------------------- |
| 1 | **[00-Overview](docs/00-overview.md)**                  | Mission, feature matrix, tech stack          |
| 2 | **[01-Installation](docs/01-installation.md)**          | pip/Poetry, extras, offline, Docker          |
| 3 | **[02-Directory Layout](docs/02-directory-layout.md)**  | src-layout tree & dev tools                  |
| 4 | **[03-Architecture](docs/03-architecture.md)**          | Component + sequence diagrams                |
| 5 | **[04-Quick Start](docs/04-usage.md)**                  | 30-line "hello world" (HTTP & Oracle)        |
| 6 | **[05-Plugin System](docs/05-plugin-system.md)**        | Hook-specs, build & publish your own adapter |
| 7 | **[06-Code-Quality Contract](docs/06-code-quality.md)** | Linters, coverage bars, CI gates             |
| 8 | **[07-Contributing](docs/07-contributing.md)**          | PR flow, ADRs, commit style                  |
| 9 | **[08-Roadmap](docs/08-roadmap.md)**                    | Version targets & long-term vision           |
| 10| **[09-Advanced Libraries](docs/09-advanced-libraries.md)** | Library usage patterns & best practices    |

> Looking to contribute? Check **[07-Contributing](docs/07-contributing.md)** for our workflow.

---

## ✨ Feature Highlights

* **Multi-Protocol Client** – HTTP 1.1/2, Oracle/PostgreSQL/SQLite, LDAP v3 (core).
* **Dynamic Entity API** – CRUD + auto-pagination & sorting.
* **Schema Toolkit** – Cache OpenAPI/JSON-Schema → generate Pydantic models.
* **CLI** – `dcapix request`, `dcapix schema`, `dcapix entity`, `dcapix config`.
* **Robust Extras** – Oracle OIC / WMS connectors, Redis cache hook, Keycloak (roadmap).

---

## 🚀 Install   *(see full guide [01-Installation](/docs/01-installation.md))*

```bash
# Core
pip install dc-api-x

# Core + Oracle DB + LDAP connectors
pip install dc-api-x[oracle-db,ldap]

# Dev environment (lint + tests + docs)
pip install dc-api-x[dev,all]
```

---

## 🔥 5-Minute Demo   *(step-by-step: [04-Quick Start](/docs/04-usage.md))*

```python
import dc_api_x as apix; apix.enable_plugins()

# HTTP call
api = apix.ApiClient(url="https://api.example.com",
                     auth_provider=apix.BasicAuthProvider("user", "pass"))
print(len(api.get("users").data))

# Oracle query (from plugin)
ora = apix.get_adapter("oracle_db_atp")
print("Rows:", ora.query_value("SELECT COUNT(*) FROM users"))
```

Run **`make run-example example=rest_api_client`** for a fuller script.

---

## 🧩 Build Your Own Connector   *(tutorial: [05-Plugin System](/docs/05-plugin-system.md))*

```python
# dc_api_x_redis/__init__.py
def register_adapters(reg):
    from .redis_adapter import RedisAdapter
    reg["redis"] = RedisAdapter
```

```toml
[project.entry-points."dc_api_x.plugins"]
redis = "dc_api_x_redis"
```

`pip install dc-api-x-redis` → `apix.enable_plugins()` → done.

---

## 🧪 Test & Lint   *(quality rules: [06-Code-Quality Contract](/docs/06-code-quality.md))*

```bash
# Run all tests with coverage
make test

# Run lint checks
make lint

# Auto-fix lint issues
make lint-fix

# Format code 
make format

# Generate lint reports
make lint-report

# Automated lint-fix cycle (highly recommended)
./scripts/auto_lint_fix.sh
```

Green CI is mandatory for every PR.

---

## 🛠️ Code Quality Tools

dc-api-x maintains high code quality through a comprehensive set of tools:

| Tool | Purpose | Command |
|------|---------|---------|
| **Black** | Code formatting | `make format` |
| **isort** | Import sorting | `make format` |
| **Ruff** | Fast linting | `make lint` |
| **Mypy** | Static type checking | `make lint` |
| **Bandit** | Security scanning | `make security` |
| **Pre-commit** | Git hooks | `pre-commit run --all-files` |
| **auto_lint_fix.sh** | Automated fixing | `./scripts/auto_lint_fix.sh` |

### Automated Code Quality Workflow

For efficient development, we recommend using our automated lint-fix cycle:

```bash
# Run from project root
./scripts/auto_lint_fix.sh
```

This script:

1. Runs `make lint` to check for issues
2. If issues are found, runs `make lint-fix` and `make format`
3. Repeats the process until no issues are found or max attempts reached
4. Provides detailed output on progress and remaining issues

Options:

* `DEBUG=1 ./scripts/auto_lint_fix.sh` - Show detailed debugging output
* `MAX_CYCLES=5 ./scripts/auto_lint_fix.sh` - Set maximum number of cycles

Our linting tools help catch issues early:

* **Magic values**: Use constants instead of literals (HTTP_OK = 200)
* **Unused arguments**: Prefix with underscore (_unused_arg)
* **Complex expressions**: Break down complex logic into smaller functions
* **Missing type hints**: All public APIs are fully typed

See [Code Quality Guidelines](docs/06-code-quality.md) for best practices.

---

## 🌍 Roadmap Highlights   *(full table: [08-Roadmap](/docs/08-roadmap.md))*

* **0.2.0 (2025-Q3)** – Oracle OIC plugin, OTEL tracing
* **0.3.0 (2025-Q4)** – Keycloak adapter, Redis cache hook
* **1.0.0 (2026-Q2)** – API freeze, 24-month LTS

---

## 🤝 License

[MIT](LICENSE) © 2025 Datacosmos — Marlon Costa.
