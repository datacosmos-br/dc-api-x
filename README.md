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
| ⚙️ **Flexible configuration** | Pydantic V2.11 Settings for env vars, files, and profiles |

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
| 11| **[10-CLI Documentation](docs/10-cli-documentation.md)** | Command-line interface reference with doctyper |
| 12| **[11-Pydantic Guide](docs/11-pydantic_guide.md)** | Comprehensive guide how to use Pydantic V2.11 in this project |
| 13| **[12-Logfire Guide](docs/12-logfire.md)** | Comprehensive guide how to use Logfire for structured logging |
| 14| **[13-Typer Guide](docs/13-typer.md)** | Comprehensive guide how to use Typer and doctyper for CLI development |
| 15| **[14-Pytest Guide](docs/14-pytest.md)** | Comprehensive guide for testing with pytest in this project |
| 16| **[15-Pluggy Guide](docs/15-pluggy.md)** | Comprehensive guide for plugin development with pluggy |

> Looking to contribute? Check **[07-Contributing](docs/07-contributing.md)** for our workflow.

---

## ✨ Feature Highlights

* **Multi-Protocol Client** – HTTP 1.1/2, Oracle/PostgreSQL/SQLite, LDAP v3 (core).
* **Dynamic Entity API** – CRUD + auto-pagination & sorting.
* **Schema Toolkit** – Cache OpenAPI/JSON-Schema → generate Pydantic models.
* **CLI** – `dcapix request`, `dcapix schema`, `dcapix entity`, `dcapix config`.
* **Robust Extras** – Oracle OIC / WMS connectors, Redis cache hook, Keycloak (roadmap).
* **Enhanced CLI Documentation** – Google-style docstrings to Typer help text with doctyper.
* **Flexible Configuration** – Environment variables, files, and profiles using Pydantic V2.11 Settings.
* **Structured Logging** – Comprehensive logging with Logfire integration for observability.
* **Plugin System** – Extensible architecture using pluggy for seamless integration of new protocols.
* **Testing Framework** – Robust testing with pytest for unit, integration, and functional tests.

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

## ⚙️ Configuration with Pydantic Settings

dc-api-x uses Pydantic Settings for flexible configuration management:

```python
# Load from environment variables
from dc_api_x.config import Config
config = Config()  # Reads API_URL, API_USERNAME, etc.

# Load from a specific profile
dev_config = Config.from_profile("dev")  # Uses .env.dev file

# Save configuration to a file
config.save("config.json")

# Load from a file
config = Config.from_file("config.json")
```

Key features:

* Environment variables with custom prefixes
* Multiple configuration profiles for different environments
* Secure handling of sensitive information with SecretStr
* Save/load configurations to/from files
* Validation and conversion of configuration values

See our [Pydantic Guide](docs/11-pydantic_guide.md) for detailed usage.

---

## 🧩 Build Your Own Connector   *(tutorial: [05-Plugin System](/docs/05-plugin-system.md) and [15-Pluggy Guide](/docs/15-pluggy.md))*

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

## 🖥️ Enhanced CLI with doctyper

dc-api-x features a rich command-line interface (CLI) enhanced with doctyper:

```bash
# Get overall help
dcapix --help

# List configuration profiles
dcapix config list

# Test API connection with specific profile
dcapix config test --profile dev

# Extract schema for an entity
dcapix schema extract customer --profile prod
```

Key benefits of our doctyper enhancement:

* **Google-style docstring parsing** - Documentation written once in code automatically appears in CLI help
* **Type-aliased identifiers** - Clear type information in help text
* **Rich formatting** - Beautiful CLI interface with proper help text and argument descriptions
* **Required vs. optional distinction** - Clear indication of which arguments are required

Learn more in our [CLI Documentation](docs/10-cli-documentation.md) and [Typer Guide](docs/13-typer.md).

---

## 🧪 Test & Lint   *(quality rules: [06-Code-Quality Contract](/docs/06-code-quality.md) and [14-Pytest Guide](/docs/14-pytest.md))*

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

## 🔍 Type Management with MonkeyType

dc-api-x integrates MonkeyType for runtime type discovery and application. This helps maintain high-quality type annotations throughout the codebase.

### What is MonkeyType?

MonkeyType is a tool that collects runtime types during test execution and helps apply them to your Python code. It's particularly useful for:
- Discovering types in legacy code
- Verifying and improving existing type annotations
- Helping with the transition to typed Python

### Using MonkeyType via Makefile

```bash
# Run tests with MonkeyType enabled to collect runtime types
make monkeytype-run

# List modules with collected type information
make monkeytype-list

# Apply collected types to a specific module
make monkeytype-apply MODULE=dc_api_x.config

# Apply collected types to all modules with available type information
make monkeytype-apply-all

# Generate a type stub (.pyi file) for a specific module
make monkeytype-stub MODULE=dc_api_x.utils.logging
```

### Benefits of Type Annotations

- Enhanced code documentation
- Better IDE support with accurate auto-completion
- Early error detection via static type checking
- Improved code maintainability

Type annotations, combined with mypy static type checking, help catch issues before runtime and improve the overall code quality.

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

## 📦 Future Plugin Ecosystem

DCApiX is expanding its ecosystem with a range of specialized plugins. See the [Pluggy Guide](docs/15-pluggy.md) for detailed information about our plugin system.

### Coming Soon (2025-2026)

| Category | Planned Plugins |
|----------|----------------|
| **HTTP & APIs** | HTTPX (HTTP/2, async), OSQuery (system monitoring) |
| **Databases & Directories** | Enhanced SQLAlchemy, Multiple LDAP libraries (ldap3, python-ldap, Ldaptor) |
| **Data Pipelines** | Singer spec, Meltano integration, ETL tooling |
| **Infrastructure** | Steampipe, Powerpipe, Flowpipe, Tailpipe |

Each plugin will follow DCApiX's architecture principles with comprehensive documentation, tests, and examples. These additions will further enhance DCApiX's capabilities as a unified integration hub for diverse protocols and services.

---

## 🔧 CI/CD Setup

> **Note:** GitHub workflow files (`.github/workflows/*`) need to be added to the repository manually through the GitHub interface. This is because pushing these files requires the `workflow` scope in OAuth permissions. The original workflow files include:
> 
> * `bump.yml`: Version bumping and changelog management
> * `lint.yml`: Code quality checks for PRs
>
> If you're contributing to this project, please ensure your OAuth token has the appropriate permissions or add the workflow files through the GitHub web interface.

---

## 🤝 License

[MIT](LICENSE) © 2025 Datacosmos — Marlon Costa.

## Development Tools

DC-API-X uses various tools to ensure code quality:

* **Black** and **isort** for formatting
* **Ruff** and **mypy** for linting and type checking
* **pytest** for testing
* **MonkeyType** for collecting and applying runtime types

### Automatic Type Discovery with MonkeyType

The project includes integration with MonkeyType, which helps discover runtime types during test execution. This makes it easier to add type annotations to code, especially for complex projects or those with many external dependencies.

```bash
# Run tests with MonkeyType to collect types
make monkeytype-run

# Apply collected types to a module
make monkeytype-apply MODULE=dc_api_x.config
```

For more details, see the [MonkeyType Usage Guide](docs/monkeytype_guide.md).
