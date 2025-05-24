# dc-api-x · Data Client API with Extensions 🚀
>
> **The Datacosmos integration ecosystem** – one import, one client, one CLI, every protocol.

DCApiX is a comprehensive Python integration ecosystem that combines a powerful framework, an extensible CLI tool, and a rich plugin architecture. It transforms how developers interact with multiple data sources, APIs, and protocols by providing a unified platform for all integration needs.

## Beyond Just a Framework

DCApiX delivers three complementary components that work together:

1. **Core Framework**: A unified client interface that abstracts away implementation details of diverse protocols
2. **Command-Line Interface (CLI)**: A rich terminal tool for direct interaction with any connected system
3. **Plugin Ecosystem**: Extensible adapters for new protocols and systems without modifying core code

This holistic approach means you can use DCApiX as a programmatic library in your applications, as a CLI tool for direct operations and testing, or as a foundation to build custom integration plugins—all with the same consistent patterns and high-quality standards.

## What DCApiX Solves

Modern data applications often need to connect to diverse systems - REST APIs, databases, LDAP directories, message queues, and cloud services. Without DCApiX, this typically means:

* Learning multiple client libraries with different patterns and conventions
* Writing boilerplate code for authentication, error handling, and data transformation
* Managing inconsistent response formats and pagination mechanisms
* Implementing type safety and validation manually for each integration
* Dealing with observability and security in a fragmented way
* Building custom CLI tools for each integration point
* Creating proprietary plugin systems for extensibility

DCApiX solves these challenges by providing a unified, type-safe, and extensible platform across all these protocols, with enterprise-grade features built in.

## Key Capabilities

| &nbsp; | Highlight |
|-------|-----------|
| 🔗 **Unified access** | Single `ApiClient` façade, plug-in adapters (HTTP, Oracle, LDAP …) |
| 🛡️ **Type-safe** | `pydantic.BaseModel` everywhere, `mypy --strict` green |
| 🧩 **Drop-in plugins** | `pluggy` entry-points → add connectors without touching the core |
| 🖥️ **Powerful CLI** | `dcapix` command suite for direct protocol interaction and testing |
| 📈 **Observability** | Structured JSON/Rich logs, OpenTelemetry spans, Prom-ready metrics |
| 🏢 **Enterprise-grade** | PEP 8, `ruff`, `bandit`, ≥ 90 % coverage, ADR workflow |
| 📜 **MIT & SemVer** | SPDX headers, changelog gated |
| ⚙️ **Flexible configuration** | Pydantic Settings for env vars, files, and profiles |

**PyPI:** `dc-api-x`   **Import:** `import dc_api_x as apix`   **CLI:** `dcapix`

```python
# As a framework
import dc_api_x as apix

# Or use the CLI
# $ dcapix request get users --profile prod
```

---

## 📚 Documentation Map

| Category | Documents |
|----------|-----------|
| **Getting Started** | [01 - Overview](docs/01-overview.md)<br>[02 - Installation](docs/02-installation.md)<br>[03 - Project Structure](docs/03-project-structure.md)<br>[04 - Architecture](docs/04-architecture.md)<br>[05 - Quickstart](docs/05-quickstart.md)<br>[06 - Roadmap](docs/06-roadmap.md) |
| **Development** | [10 - Development: Code Quality](docs/10-development-code-quality.md)<br>[11 - Development: Contributing](docs/11-development-contributing.md)<br>[12 - Development: Plugin System](docs/12-development-plugin-system.md) |
| **Technology Guides** | [20 - Tech: Pydantic](docs/20-tech-pydantic.md)<br>[21 - Tech: Logfire](docs/21-tech-logfire.md)<br>[22 - Tech: Typer](docs/22-tech-typer.md)<br>[23 - Tech: Testing](docs/23-tech-testing.md)<br>[24 - Tech: Pluggy](docs/24-tech-pluggy.md)<br>[25 - Tech: Advanced Libraries](docs/25-tech-advanced-libraries.md)<br>[26 - Tech: MonkeyType](docs/26-tech-monkeytype.md)<br>[25 - Tech: Typing](docs/25-tech-typing.md) |
| **References** | [30 - CLI Reference](docs/30-cli-reference.md) |
| **Integration** | [40 - Integration: Robot Framework](docs/40-integration-robot-framework.md)<br>[41 - Integration: Data Processing](docs/41-integration-data-processing.md)<br>[42 - Integration: Oracle OCI](docs/42-integration-oracle-oci.md)<br>[43 - Integration: Amazon AWS](docs/43-integration-amazon-aws.md)<br>[44 - Integration: Google Cloud](docs/44-integration-google-cloud.md)<br>[45 - Integration: Microsoft Azure](docs/45-integration-microsoft-azure.md)<br>[46 - Integration: Kubernetes](docs/46-integration-kubernetes.md) |

> Looking to contribute? Check **[11 - Development: Contributing](docs/11-development-contributing.md)** for our workflow.

---

## ✨ Feature Highlights

* **Multi-Protocol Client** – HTTP 1.1/2, Oracle/PostgreSQL/SQLite, LDAP v3 (core).
* **Dynamic Entity API** – CRUD + auto-pagination & sorting.
* **Schema Toolkit** – Cache OpenAPI/JSON-Schema → generate Pydantic models.
* **CLI** – `dcapix request`, `dcapix schema`, `dcapix entity`, `dcapix config`.
* **Robust Extras** – Oracle OIC / WMS connectors, Redis cache hook, Keycloak (roadmap).
* **Enhanced CLI Documentation** – Google-style docstrings to Typer help text with doctyper.
* **Flexible Configuration** – Environment variables, files, and profiles using Pydantic Settings.
* **Structured Logging** – Comprehensive logging with Logfire integration for observability.
* **Plugin System** – Extensible architecture using pluggy for seamless integration of new protocols.
* **Testing Framework** – Robust testing with pytest for unit, integration, and functional tests.
* **Type Discovery** – MonkeyType integration for automatic type annotation generation and Pydantic field type discovery.

---

## 🚀 Install   *(see full guide [02 - Installation](/docs/02-installation.md))*

```bash
# Core
pip install dc-api-x

# Core + Oracle DB + LDAP connectors
pip install dc-api-x[oracle-db,ldap]

# Dev environment (lint + tests + docs)
pip install dc-api-x[dev,all]
```

---

## 🔥 5-Minute Demo   *(step-by-step: [05 - Quickstart](/docs/05-quickstart.md))*

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

See our [20 - Tech: Pydantic](docs/20-tech-pydantic.md) guide for detailed usage.

---

## 🧩 Build Your Own Connector   *(tutorial: [12 - Development: Plugin System](/docs/12-development-plugin-system.md) and [24 - Tech: Pluggy](/docs/24-tech-pluggy.md))*

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

Learn more in our [30 - CLI Reference](docs/30-cli-reference.md) and [22 - Tech: Typer](docs/22-tech-typer.md) guides.

---

## 🧪 Test & Lint   *(quality rules: [10 - Development: Code Quality](/docs/10-development-code-quality.md) and [23 - Tech: Testing](/docs/23-tech-testing.md))*

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

* Discovering types in legacy code
* Verifying and improving existing type annotations
* Helping with the transition to typed Python

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

* Enhanced code documentation
* Better IDE support with accurate auto-completion
* Early error detection via static type checking
* Improved code maintainability

Type annotations, combined with mypy static type checking, help catch issues before runtime and improve the overall code quality.

For more details, see the [26 - Tech: MonkeyType](docs/26-tech-monkeytype.md) guide for comprehensive MonkeyType integration documentation.

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

See [10 - Development: Code Quality](docs/10-development-code-quality.md) for best practices.

---

## 🌍 Roadmap Highlights   *(full table: [06 - Roadmap](/docs/06-roadmap.md))*

* **0.2.0 (2025-Q3)** – Oracle OIC plugin, OTEL tracing
* **0.3.0 (2025-Q4)** – Keycloak adapter, Redis cache hook
* **1.0.0 (2026-Q2)** – API freeze, 24-month LTS

---

## 📦 Future Plugin Ecosystem

DCApiX is expanding its ecosystem with a range of specialized plugins. See the [24 - Tech: Pluggy](docs/24-tech-pluggy.md) guide for detailed information about our plugin system.

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

---

## Quick Links

* [Security Policy](SECURITY.md)
* [Changelog](CHANGELOG.md)
* [Code of Conduct](CODE_OF_CONDUCT.md)
* [Support](docs/11-development-contributing.md#getting-support)
* [Contribution Guidelines](docs/11-development-contributing.md)

---

**Made with ❤️ by Datacosmos Engineering.**

# Type System Updates

The type system has been modernized to use Python 3.10+ type annotation features:

* Replaced `Optional[X]` with `X | None` syntax (PEP 604)
* Replaced `Union[A, B]` with `A | B` union operator
* Added central `type_definitions.py` for common type definitions
* Updated Protocol classes for better structural typing
* Improved handling of circular imports with `TYPE_CHECKING`
* Enhanced TypeVar and Generic usage

See the updated documentation in [docs/25-tech-typing.md](docs/25-tech-typing.md) for details on the type system.

## Type Definitions

Common types are now defined in a central location:

```python
# Common JSON-related types
JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]

# HTTP related types
Headers = dict[str, str]
HttpMethod = str  # GET, POST, PUT, PATCH, DELETE
StatusCode = int

# Entity related types
EntityId = str | int  # Common ID types
```
