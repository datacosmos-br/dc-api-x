# dc-api-x

## Data Client API Extensions

**dc-api-x** is the Datacosmos integration ecosystem that turns Python into a **multi-protocol integration hub**—capable of speaking HTTP/REST, relational databases, LDAP directories, message queues, caches, and whatever comes next.

### What is DCApiX?

DCApiX is not just a framework—it's a complete integration ecosystem that combines three powerful components:

1. **Core Framework**: A unified client interface that abstracts away protocol-specific implementations
2. **Command-Line Interface (CLI)**: A rich terminal tool for direct interaction with any connected system
3. **Plugin Ecosystem**: Extensible adapters for new protocols and systems without modifying core code

This ecosystem approach allows developers to use DCApiX as a programmatic library in applications, as a CLI tool for operations and testing, or as a foundation for building custom integration plugins—all with consistent patterns and enterprise-grade quality.

### The Integration Challenge

Data engineers and developers typically face these challenges when building integrations:

* **Protocol Proliferation**: Each system requires different client libraries with unique patterns
* **Boilerplate Overload**: Authentication, error handling, and pagination code is repeated across projects
* **Type Safety Gaps**: Raw API responses require manual validation and transformation
* **CLI Fragmentation**: Separate command-line tools needed for each protocol or system
* **Observability Blind Spots**: Difficult to track and monitor diverse connection types consistently
* **Plugin Complexity**: Extending systems with new protocols often requires core code changes
* **Configuration Sprawl**: Managing connection parameters across environments becomes unwieldy

DCApiX addresses these challenges through its unified design, robust type system, CLI tooling, and extensible plugin architecture—providing a complete solution for modern integration needs.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [README](../README.md) | **01 - Overview** | [02 - Installation](02-installation.md) |

---

## Mission Statement

> *"One import. One client. One CLI. Everything connected—without boilerplate."*

DCApiX eliminates repetitive plumbing code, enforces enterprise-grade quality gates, and lets teams plug new connectors in minutes, not days—whether accessed programmatically or through the command line.

---

## Why It Matters 📈

| Key Goal | How dc-api-x Delivers |
|----------|-----------------------|
| **Unified access** | A single `ApiClient` façade backed by protocol-specific **Adapters** (HTTP, SQLAlchemy, `ldap3`, MQ, Redis …). |
| **Type safety** | All payloads, configs, and entity schemas inherit `pydantic.BaseModel` from Pydantic &rightarrow; instant validation + IDE autocompletion. |
| **Drop-in extensibility** | `pluggy` hook-specs let you ship new connectors as independent wheels—zero changes to the core package. |
| **Observability** | Built-in structured logging via **Logfire**, tracing hooks for **OpenTelemetry**, and metrics-ready middleware. |
| **Resilience** | `tenacity`-powered retries, circuit-breaker hooks, connection pooling, timeout guards. |
| **Security first** | Secrets via `python-dotenv` / OS env vars, TLS everywhere, pluggable auth (Basic, Token, OAuth2, mTLS). |
| **Enterprise quality** | 100 % PEP 8, strict `mypy --strict`, `ruff`, `bandit`; CI enforces ≥ 90 % unit-test coverage with **pytest**. |
| **Governance** | SemVer, SPDX headers, MIT license, CHANGELOG "Keep a Changelog" format. |
| **Zero-friction DX** | Ready-to-use CLI (`dcapix`) powered by **Typer** and **doctyper**, Makefile targets, Poetry src-layout, example gallery. |

> **PyPI name:** `dc-api-x`  **Import:** `import dc_api_x as apix`

---

## High-Level Feature Matrix 🧩

| Category | Highlights |
|----------|------------|
| **Protocols (core)** | HTTP/HTTPS (sync & async), JDBC-style SQL (via SQLAlchemy 2), LDAP v3. |
| **Official Plugins** | Oracle DB, Oracle OIC, Oracle WMS, Keycloak, Redis, Kafka (roadmap). |
| **Hook Pipeline** | Request/Response/Error hooks: Retry ↔ Cache ↔ Audit ↔ Auth ↔ Transform. |
| **Schema Layer** | Automatic OpenAPI / JSON-Schema extraction → cached local models. |
| **Entity API** | CRUD + custom actions with pagination, sorting, filtering abstractions. |
| **Pagination** | Offset, cursor, header-based, or "has-more + next-page" handled transparently. |
| **Config system** | Hierarchical: Env vars, .env files, TOML, JSON, profiles and more via [Pydantic Guide](20-tech-pydantic.md). |
| **CLI Toolbox** | `dcapix request`, `dcapix schema`, `dcapix entity`, `dcapix config test` built with [Typer Guide](22-tech-typer.md). |
| **Observability** | Structured logs with [Logfire Guide](21-tech-logfire.md), optional OTEL spans (`TRACE_ID` logged automatically). |
| **Plugin System** | Extensible architecture using [Pluggy Guide](24-tech-pluggy.md) for seamless integration of new protocols. |
| **Testing** | Comprehensive test suite using [Testing Guide](23-tech-testing.md) for unit, integration, and functional tests. |
| **Testing Aids** | Built-in `apix.testing.MockAdapter` + `responses` for offline unit tests. |

---

## Core Building Blocks 🔧

| Layer | Responsibility |
|-------|----------------|
| **ApiClient** | High-level façade exposing `get/post/put/delete` for REST **or** `query/execute` for databases. |
| **Adapters** | Low-level protocol drivers (`HttpAdapter`, `DatabaseAdapter`, `DirectoryAdapter`, …). |
| **Auth Providers** | Encapsulate credential storage and header/handshake injection. |
| **Hooks** | Middleware chain (pre-request, post-response, error). |
| **Providers** | Domain helpers: `DataProvider`, `SchemaProvider`, `TransformProvider`, `ConfigProvider`. |
| **Plugin Manager** | Discovers & registers third-party packages via entry-points `dc_api_x.plugins` using pluggy. |
| **Config** | Modern configuration system based on Pydantic Settings with multiple sources and profiles. |
| **Logging** | Structured logging with Logfire for comprehensive observability across all components. |
| **CLI** | Command-line interface built with Typer and enhanced with doctyper for rich documentation. |
| **Testing** | Robust testing infrastructure with pytest and specialized fixtures for protocol testing. |

---

## Supported Workflows 🚀

* **ETL**: Stream data from Oracle WMS → Oracle ADB using async pagination & batch insert.
* **IAM Sync**: Mirror corporate LDAP into Keycloak via bulk user management endpoints.
* **Observability**: Push OpenTelemetry spans into Grafana Cloud with built-in OTLP exporter.
* **Automation**: Run "config drift" checks on 300+ environments in parallel with asyncio adapters.

See the `examples/` directory for reproducible scripts.

---

## Future Plugin Ecosystem 🔌

DCApiX is committed to expanding its plugin ecosystem to support an ever-growing range of protocols, data sources, and integration patterns. Our future roadmap includes:

### HTTP and API Enhancements

* **HTTPX Plugin** - Modern HTTP client with HTTP/2 and async support
* **OSQuery Integration** - Extending DCApiX to system-level monitoring via SQL

### Advanced Database and Directory Support

* **Enhanced SQLAlchemy Integration** - Custom types, dialects, and connection instrumentation
* **Multiple LDAP Client Options** - ldap3, python-ldap, and Ldaptor support for diverse LDAP needs

### Data Pipeline Solutions

* **Singer Specification** - Standard ETL taps and targets for seamless data flow
* **Meltano Integration** - ELT framework with pipeline orchestration
* **ETL SDK** - Tools for building custom extractors and loaders

### Infrastructure Management

* **Steampipe/Powerpipe** - SQL querying across cloud services and metrics visualization
* **Flowpipe/Tailpipe** - Workflow automation and data transformation

For detailed descriptions, expected release dates, and technical features, see the [Plugin Roadmap](24-tech-pluggy.md#future-plugin-roadmap) in our Pluggy Guide.

---

## Quick Taste 🍿

```python
import dc_api_x as apix

apix.enable_plugins()                 # loads oracle_db, ldap, etc.

# --- WMS API --------------------------------------------------------------
wms = apix.ApiClient.from_profile("wms_hml")
for order in wms.paginate("order_hdr", params={"status": "SHIPPED"}):
    print(order.order_nbr)

# --- Oracle Autonomous DB -------------------------------------------------
ora = apix.get_adapter("oracle_db_atp")
total = ora.query_value("select count(*) from wms_orders")
print("Rows in ADB:", total)

# --- LDAP Directory -------------------------------------------------------
ldap = apix.get_adapter("corp_ldap")
users = ldap.search("ou=People,dc=example,dc=com", "(mail=*@datacosmos.com.br)")
print("LDAP users:", len(users))

# --- Configuration with Pydantic Settings ---------------------------------
from dc_api_x.config import Config

# Load from environment variables (API_URL, API_USERNAME, etc.)
config = Config()

# Or load from a specific profile
dev_config = Config.from_profile("dev")  # Uses .env.dev file

# Save configuration to JSON
config.save("my_config.json")

# --- Structured Logging with Logfire ---------------------------------------
import logfire

# Configure Logfire with service details
logfire.configure(service_name="dc-api-x", environment="dev")

# Log structured information
with logfire.context(request_id="req-123"):
    logfire.info("Processing order", order_id="ORD-456", items_count=5)
```

---

## When NOT to Use dc-api-x ❓

| Scenario                                              | Alternative                                                                  |
| ----------------------------------------------------- | ---------------------------------------------------------------------------- |
| Pure data-science work inside a Jupyter notebook      | Use `requests` or DB-specific clients directly to avoid added complexity.    |
| Ultra-high-throughput event pipelines (≥ 100 k msg/s) | Consider language-native drivers (Kafka ✅, but maybe Rust for extreme perf). |
| Front-end / browser integrations                      | dc-api-x targets server-side Python; use the language best suited for UI.    |

---

## Documentation Map

| Category | Documents |
|----------|-----------|
| **Getting Started** | [01 - Overview](01-overview.md) (this document)<br>[02 - Installation](02-installation.md)<br>[03 - Project Structure](03-project-structure.md)<br>[04 - Architecture](04-architecture.md)<br>[05 - Quickstart](05-quickstart.md)<br>[06 - Roadmap](06-roadmap.md) |
| **Development** | [10 - Development: Code Quality](10-development-code-quality.md)<br>[11 - Development: Contributing](11-development-contributing.md)<br>[12 - Development: Plugin System](12-development-plugin-system.md) |
| **Technology Guides** | [20 - Tech: Pydantic](20-tech-pydantic.md)<br>[21 - Tech: Logfire](21-tech-logfire.md)<br>[22 - Tech: Typer](22-tech-typer.md)<br>[23 - Tech: Testing](23-tech-testing.md)<br>[24 - Tech: Pluggy](24-tech-pluggy.md)<br>[25 - Tech: Advanced Libraries](25-tech-advanced-libraries.md) |
| **References** | [30 - CLI Reference](30-cli-reference.md) |
| **Integration** | [40 - Integration: Robot Framework](40-integration-robot-framework.md)<br>[41 - Integration: Data Processing](41-integration-data-processing.md)<br>[42 - Integration: Oracle OCI](42-integration-oracle-oci.md)<br>[43 - Integration: Amazon AWS](43-integration-amazon-aws.md)<br>[44 - Integration: Google Cloud](44-integration-google-cloud.md)<br>[45 - Integration: Microsoft Azure](45-integration-microsoft-azure.md)<br>[46 - Integration: Kubernetes](46-integration-kubernetes.md) |

---

## Next Steps

1. **Install** → `pip install dc-api-x[dev]` ([Installation Guide](02-installation.md))
2. **Read the rest of the docs** for setup, plugin creation and CI pipeline
3. **Check out our technology guides:**
   * [Pydantic Guide](20-tech-pydantic.md) for advanced configuration options
   * [Logfire Guide](21-tech-logfire.md) for structured logging and observability
   * [Typer Guide](22-tech-typer.md) for CLI development with doctyper
   * [Testing Guide](23-tech-testing.md) for testing strategies and best practices
   * [Pluggy Guide](24-tech-pluggy.md) for developing plugins and extensions
4. **Star the repo ⭐** if it saves you time!

---

**Made with ❤️ by Datacosmos Engineering.**
