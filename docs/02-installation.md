# Installation Guide

> ```bash
> # Core
> pip install dc-api-x
>
> # Core + Oracle DB + LDAP
> pip install dc-api-x[oracle-db,ldap]
> ```

dc-api-x ships as a set of pure-Python wheels published to PyPI. Build tools required: **Python ≥ 3.10** and **pip ≥ 23.0**.

---

## 1  Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python** | CPython 3.10 → 3.12 (full support) &nbsp;•&nbsp; PyPy 3.10 (best-effort, **no Oracle driver**) |
| **Operating System** | Linux, macOS, Windows. Linux x64 is what Datacosmos runs in CI. |
| **Compiler** | *Not needed* — all dependencies ship as wheels. |
| **Oracle Thick mode** (optional) | Instant Client ≥ 21; set `LD_LIBRARY_PATH`/`PATH` accordingly. |

Always install inside a virtual environment (`venv`, **pyenv**, **conda**, or **pipx**) to avoid system-site pollution.

---

## 2  Core Installation

```bash
python -m pip install --upgrade pip          # make sure pip is recent
pip install dc-api-x
```

Verify:

```bash
python - <<'PY'
import dc_api_x as apix, sys, platform
print("dc-api-x version:", apix.__version__)
print("Python:", sys.version)
print("OS:", platform.platform())
PY
```

---

## 3  Installing Extras

dc-api-x ships optional "extras" that pull in heavy or licensing-sensitive dependencies only on demand.

| Extra flag   | Installs                                       | Notes                                                          |
| ------------ | ---------------------------------------------- | -------------------------------------------------------------- |
| `oracle-db`  | `python-oracledb`, `dc-api-x-oracle-db` plugin | Thin mode by default; thick mode if Instant Client is present. |
| `oracle-oic` | `dc-api-x-oracle-oic`                          | Adds Oracle Integration Cloud connector.                       |
| `oracle-wms` | `dc-api-x-oracle-wms`                          | Adds Oracle Warehouse Management Cloud connector.              |
| `ldap`       | `ldap3`, `dc-api-x-ldap`                       | Generic LDAP/AD adapter with StartTLS & DirSync.               |
| `all`        | *Everything above*                             | Kitchen-sink install for power users.                          |

### Example

```bash
# HTTP + Oracle DB + LDAP
pip install dc-api-x[oracle-db,ldap]
```

After installation:

```python
import dc_api_x as apix
apix.enable_plugins()             # discovers oracle_db & ldap
```

---

## 4  Development Setup

Clone the repository and install **all** dev tools:

```bash
git clone https://github.com/datacosmos/dc-api-x.git
cd dc-api-x
# Full dev env: core + extras + linters + test stack
pip install -e .[all,dev,docs,examples]
pre-commit install          # git hooks (black, ruff, mypy, etc.)
pytest -q                   # run unit tests
```

Using **Poetry** instead?

```bash
poetry install -E all
poetry run pytest
```

---

## 5  Running via Docker (optional)

```bash
docker build -t dcapix-sandbox .
docker run -it --rm dcapix-sandbox python -m dcapix config list
```

The provided `Dockerfile` copies your local `pyproject.toml`, installs the requested extras, and exposes the `dcapix` CLI.

---

## 6  Upgrading

```bash
pip install --upgrade dc-api-x         # core
pip install --upgrade "dc-api-x[all]"  # core + every extra
```

`pip list --outdated` will show if any plugin wheels need renewal as well.

---

## 7  Offline / Air-gapped Environments

1. On a machine with internet access:

   ```bash
   pip download dc-api-x[all] -d /tmp/wheels
   ```

2. Transfer the `/tmp/wheels` folder to the target network.
3. Install:

   ```bash
   pip install --no-index --find-links=/tmp/wheels dc-api-x[all]
   ```

---

## 8  Post-install Checklist ✅

| Task                    | Command                                                                                   |
| ----------------------- | ----------------------------------------------------------------------------------------- |
| Basic smoke test        | `python -m dc_api_x.cli --help`                                                           |
| Verify plugin discovery | `python - <<'PY'\nimport dc_api_x as x; x.enable_plugins(); print(x.list_adapters())\nPY` |
| Run example             | `python examples/rest_api_client.py`                                                      |
| Generate docs           | `make docs` (requires `mkdocs` or Sphinx extras)                                          |

---

## 9  Troubleshooting

| Symptom                                                    | Fix                                                                                    |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: dc_api_x_oracle_db`                  | Install the correct extra: `pip install dc-api-x[oracle-db]`                           |
| `DPI-1047: Cannot locate Oracle Client`                    | Use thin mode (default) or set `LD_LIBRARY_PATH` to Instant Client directory.          |
| `ValueError: No plugin provides adapter "oracle_wms_prod"` | Call `apix.enable_plugins()` **after** plugins are installed.                          |
| SSL/TLS verify errors behind proxy                         | `export REQUESTS_CA_BUNDLE=/path/to/ca.pem` or pass `verify_ssl=False` in `ApiClient`. |

---

Happy hacking, and may your integrations be boring 🎉
