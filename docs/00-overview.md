# dc-api-x  

## Data Client API Extensions

**dc-api-x** is the Datacosmos framework that turns Python into a **multi-protocol integration hub**—capable of speaking HTTP/REST, relational databases, LDAP directories, message queues, caches, and whatever comes next.

---

## Mission Statement

> *"One import. One client. Everything connected—without boilerplate."*

dc-api-x eliminates repetitive plumbing code, enforces enterprise-grade quality gates, and lets teams plug new connectors in minutes, not days.

---

## Why It Matters 📈

| Key Goal | How dc-api-x Delivers |
|----------|-----------------------|
| **Unified access** | A single `ApiClient` façade backed by protocol-specific **Adapters** (HTTP, SQLAlchemy, `ldap3`, MQ, Redis …). |
| **Type safety** | All payloads, configs, and entity schemas inherit `pydantic.BaseModel` v2 &rightarrow; instant validation + IDE autocompletion. |
| **Drop-in extensibility** | `pluggy` hook-specs let you ship new connectors as independent wheels—zero changes to the core package. |
| **Observability** | Built-in JSON logs (`structlog`), tracing hooks for **OpenTelemetry**, and metrics-ready middleware. |
| **Resilience** | `tenacity`-powered retries, circuit-breaker hooks, connection pooling, timeout guards. |
| **Security first** | Secrets via `python-dotenv` / OS env vars, TLS everywhere, pluggable auth (Basic, Token, OAuth2, mTLS). |
| **Enterprise quality** | 100 % PEP 8, strict `mypy --strict`, `ruff`, `bandit`; CI enforces ≥ 90 % unit-test coverage. |
| **Governance** | SemVer, SPDX headers, MIT license, CHANGELOG "Keep a Changelog" format. |
| **Zero-friction DX** | Ready-to-use CLI (`dcapix`), Makefile targets, Poetry src-layout, example gallery. |

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
| **Config system** | Hierarchical: ENV › .profile.toml › CLI flags › direct kwargs. |
| **CLI Toolbox** | `dcapix request`, `dcapix schema`, `dcapix entity`, `dcapix config test`. |
| **Observability** | Structured logs, optional OTEL spans (`TRACE_ID` logged automatically). |
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
| **Plugin Manager** | Discovers & registers third-party packages via entry-points `dc_api_x.plugins`. |

---

## Supported Workflows 🚀

* **ETL**: Stream data from Oracle WMS → Oracle ADB using async pagination & batch insert.
* **IAM Sync**: Mirror corporate LDAP into Keycloak via bulk user management endpoints.
* **Observability**: Push OpenTelemetry spans into Grafana Cloud with built-in OTLP exporter.
* **Automation**: Run "config drift" checks on 300+ environments in parallel with asyncio adapters.

See the `examples/` directory for reproducible scripts.

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
```

---

## When NOT to Use dc-api-x ❓

| Scenario                                              | Alternative                                                                  |
| ----------------------------------------------------- | ---------------------------------------------------------------------------- |
| Pure data-science work inside a Jupyter notebook      | Use `requests` or DB-specific clients directly to avoid added complexity.    |
| Ultra-high-throughput event pipelines (≥ 100 k msg/s) | Consider language-native drivers (Kafka ✅, but maybe Rust for extreme perf). |
| Front-end / browser integrations                      | dc-api-x targets server-side Python; use the language best suited for UI.    |

---

## Next Steps

1. **Install** → `pip install dc-api-x[dev]`
2. **Read the rest of the docs** (`docs/*.md`) for setup, plugin creation and CI pipeline.
3. **Star the repo ⭐** if it saves you time!

---

**Made with ❤️ by Datacosmos Engineering.**
