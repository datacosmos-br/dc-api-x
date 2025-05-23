# Quick Start

The following snippets take you from **zero → API call → database query** in
less than 30 lines of code.  
All examples assume you have already run:

```bash
pip install dc-api-x
pip install dc-api-x[oracle-db]   # ← for the Oracle section
```

---

## 1  Import & Bootstrap

```python
import dc_api_x as apix  # recommended alias ≡ apix

# Discover optional plugins installed via extras
apix.enable_plugins()    # < 10 ms when no plugins present
```

---

## 2  Create a Client (HTTP)

```python
client = apix.ApiClient(
    url="https://api.example.com",
    auth_provider=apix.BasicAuthProvider("user", "pass"),
    timeout=30,              # seconds
    verify_ssl=True,         # set False only in lab envs
)
```

### 2.1  Make a GET request

```python
resp = client.get("users")   # → ApiResponse object
if resp.success:
    print("Total users:", len(resp.data))
else:
    raise RuntimeError(resp.error)
```

### 2.2  Auto-pagination

```python
for user in client.paginate("users", params={"status": "active"}, page_size=50):
    print(user["name"])
```

---

## 3  Oracle Database (Plugin Example)

> Requires `pip install dc-api-x[oracle-db]` and `apix.enable_plugins()`.

```python
ora = apix.get_adapter("oracle_db_atp")   # name from .profile or env vars
count = ora.query_value("SELECT COUNT(*) FROM users")
print("Rows in Oracle ADB:", count)
```

You can also run PL/SQL inside a managed transaction:

```python
with ora.transaction():
    ora.execute("UPDATE users SET flag = 0 WHERE flag IS NULL")
```

---

## 4  Using Configuration Profiles

### 4.1 Using Pydantic V2.11 Settings

dc-api-x uses Pydantic V2.11 Settings for flexible configuration management. You can set up configuration through environment variables, `.env` files, or JSON/TOML files.

```python
from dc_api_x.config import Config

# Load from environment variables (API_URL, API_USERNAME, etc.)
config = Config()

# Load from a specific profile (.env.dev file)
dev_config = Config.from_profile("dev")

# Save configuration to a file
config.save("my_config.json")

# Reload configuration after environment changes
config.model_reload()
```

See the [Pydantic Guide](11-pydantic_guide.md) for detailed information.

### 4.2 Traditional Profile Format

Create `~/.config/dcapix/profiles.toml`

```toml
[dev]
url = "https://api-dev.example.com"
username = "api-dev"
password = "s3cr3t"
timeout = 20
```

```python
dev_client = apix.ApiClient.from_profile("dev")
print(dev_client.get("status").data)
```

The lookup order is **CLI args > environment variables > profile > defaults**.

---

## 5  CLI in 30 seconds

```bash
# Ping an endpoint
dcapix request get /users -P url=https://api.example.com -P username=user -P password=pass

# Extract OpenAPI schemas locally
dcapix schema extract --all --out ./schemas

# List configuration profiles
dcapix config list

# Test connection with a specific profile
dcapix config test --profile dev
```

*(run `dcapix --help` for the full command tree).*

For detailed information on the CLI, see the [Typer Guide](13-typer.md).

---

## 6  Structured Logging with Logfire

DCApiX provides powerful structured logging capabilities through Logfire integration:

```python
import logfire
from dc_api_x import ApiClient

# Configure Logfire
logfire.configure(service_name="my-service", environment="dev")

# Create client with automatic request logging
client = ApiClient(url="https://api.example.com")

# Logs will include structured information about requests and responses
response = client.get("users")

# Add contextual information to logs
with logfire.context(operation="user_processing"):
    for user in response.data:
        logfire.info("Processing user", user_id=user["id"])
```

See the [Logfire Guide](12-logfire.md) for comprehensive logging documentation.

---

## 7  Async Preview (roadmap)

```python
# Experimental: will be released in v0.3
import asyncio, dc_api_x as apix

async def main():
    async with apix.ApiAsyncClient(url="https://api.example.com") as c:
        data = await c.get("users")
        print(data)

asyncio.run(main())
```

---

## 8  Where to Go Next?

* **`examples/` folder** – complete scripts for GitHub API, Oracle WMS, schema extraction.
* **Architecture doc** – deep-dive into adapters, hooks and plugin manager.
* **Contributing guide** – write your own adapter in < 100 LOC and publish it!
* **Key Guides:**
  * [Pydantic Guide](11-pydantic_guide.md) – learn about the modern configuration system
  * [Logfire Guide](12-logfire.md) – master structured logging and observability
  * [Typer Guide](13-typer.md) – build powerful CLI interfaces with doctyper

Happy hacking 🚀
