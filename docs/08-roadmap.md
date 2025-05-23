# Project Roadmap

dc-api-x follows a transparent roadmap with clear milestones and planned features.  
This document outlines what's coming next and our long-term vision.

---

## 1 ▸ Release Schedule

| Version | Target Date | Focus |
|---------|-------------|-------|
| **0.2.0** | 2025-Q3 | Oracle OIC plugin, OTEL tracing |
| **0.3.0** | 2025-Q4 | Keycloak adapter, Redis cache hook |
| **0.4.0** | 2026-Q1 | Async adapters, SQLAlchemy 2.0 support |
| **1.0.0** | 2026-Q2 | API freeze, 24-month LTS commitment |

We follow semantic versioning rigorously:

- **Patch** (0.x.1): Bug fixes only, no new features
- **Minor** (0.x+1.0): New features, backwards compatible 
- **Major** (x+1.0.0): Breaking changes

---

## 2 ▸ Near-Term Priorities (0.2.x)

| Feature | Status | Target |
|---------|--------|--------|
| Oracle OIC adapter | In development | 0.2.0 |
| OpenTelemetry integration | Planning | 0.2.0 |
| Prometheus metrics hook | Planning | 0.2.0 |
| Bulk entity operations | Design | 0.2.1 |
| OAuth2 provider improvements | Planning | 0.2.1 |
| SQLAlchemy 2.0 adapter | Design | 0.2.2 |

---

## 3 ▸ Medium-Term Goals (0.3.x → 0.4.x)

| Area | Planned Features |
|------|------------------|
| **Performance** | Connection pooling, response caching, batch operations |
| **Resilience** | Circuit breaker pattern, configurable backoff strategies |
| **Security** | mTLS support, credential rotation, audit logging |
| **Observability** | OTEL dashboards, structured logging enhancements |
| **APIs** | GraphQL support, AsyncAPI schema handling |
| **Plugins** | Kafka, Redis, Azure, AWS connectors |

---

## 4 ▸ Plugin Ecosystem Roadmap

DCApiX is committed to expanding its plugin ecosystem through a phased release strategy.
For more detailed information on each plugin, see the [Pluggy Guide](15-pluggy.md#future-plugin-roadmap).

### HTTP and API Enhancements (2025)

| Plugin | Description | Target Release |
|--------|-------------|----------------|
| **dc-api-x-httpx** | Modern HTTP client supporting HTTP/2, async capabilities | Q3 2025 |
| **dc-api-x-osquery** | System monitoring via SQL interface | Q4 2025 |

### Database and Directory Services (2025)

| Plugin | Description | Target Release |
|--------|-------------|----------------|
| **dc-api-x-sqlalchemy** | Enhanced SQLAlchemy integration with custom types, dialects | Q2 2025 |
| **dc-api-x-ldaptor** | Asynchronous LDAP operations | Q3 2025 |
| **dc-api-x-python-ldap** | Advanced LDAP functionality with SASL support | Q3 2025 |
| **dc-api-x-ldap3** | Comprehensive LDAP operations with connection pooling | Q2 2025 |

### Data Pipeline and ETL (2025-2026)

| Plugin | Description | Target Release |
|--------|-------------|----------------|
| **dc-api-x-singer** | Implementation of Singer ETL specification | Q4 2025 |
| **dc-api-x-meltano** | Integration with Meltano ELT framework | Q4 2025 |
| **dc-api-x-sdk-meltano** | SDK for building custom extractors/loaders | Q1 2026 |

### Infrastructure and Querying Tools (2026)

| Plugin | Description | Target Release |
|--------|-------------|----------------|
| **dc-api-x-steampipe** | SQL querying across cloud services | Q2 2026 |
| **dc-api-x-powerpipe** | Metrics collection and visualization | Q2 2026 |
| **dc-api-x-flowpipe** | Infrastructure automation and CI/CD integration | Q3 2026 |
| **dc-api-x-tailpipe** | Data transformation pipelines | Q3 2026 |

All plugins will adhere to DCApiX's architecture principles and undergo comprehensive testing before release. The development roadmap is subject to adjustment based on community feedback and evolving technology landscapes.

---

## 5 ▸ Long-Term Vision (1.0+)

Our vision for dc-api-x 1.0 and beyond:

1. **Stable Core** – Backwards compatibility guarantees and LTS support
2. **Plug-and-Play Ecosystem** – Rich ecosystem of first and third-party plugins
3. **Enterprise Ready** – Complete observability, security, and compliance features
4. **Performance Optimized** – Support for high-throughput data pipelines

The 1.0 release will mark our commitment to API stability and enterprise readiness.

---

## 6 ▸ Community Contributions

We welcome contributions in these areas:

- Additional protocol adapters (RabbitMQ, MongoDB, etc.)
- Performance optimizations
- Documentation improvements and translations
- Example projects and tutorials
- Testing infrastructure

See our [Contributing Guide](07-contributing.md) for details on how to get involved.

---

## 7 ▸ Feedback & Feature Requests

The roadmap is driven by user needs. To influence our priorities:

1. Open a GitHub issue with the "enhancement" label
2. Include a clear use case and business value
3. Consider submitting a PR with an initial implementation

We review all feature requests quarterly.

---

*This roadmap was last updated: May 2025.*
