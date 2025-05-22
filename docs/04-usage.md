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
```

*(run `dcapix --help` for the full command tree).*

---

## 6  Async Preview (roadmap)

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

## 7  Where to Go Next?

* **`examples/` folder** – complete scripts for GitHub API, Oracle WMS, schema extraction.
* **Architecture doc** – deep-dive into adapters, hooks and plugin manager.
* **Contributing guide** – write your own adapter in < 100 LOC and publish it!

Happy hacking 🚀
