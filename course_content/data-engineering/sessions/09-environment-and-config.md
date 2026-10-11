# Session 9 · Environment variables and config files

## The big idea

The same pipeline runs on your laptop, in testing and in production, but with **different
settings**: a different database, a different API key, a different output folder. Those settings
must live **outside** the code:

- **Config files** hold settings that are safe to share and commit to Git (paths, batch sizes,
  schedules).
- **Environment variables** hold anything that changes per machine, and **every secret** (passwords,
  API keys), which must never be committed.

**Everyday example:** a recipe (code) is the same in every branch of a restaurant chain, but each
branch has its own supplier and its own safe code. Those go on a card in the branch, not in the
recipe book.

Run the examples in order.

```{raw} html
:file: ../diagrams/s09-config.html
```

## Environment variables

Every process has a set of `NAME=value` strings it inherits from where it was started. In the
terminal you set one with `export SHOP_DB_HOST=localhost` (Linux/macOS) or
`$env:SHOP_DB_HOST="localhost"` (PowerShell). In Python they're in `os.environ`:

```python
import os

os.environ["SHOP_DB_HOST"] = "localhost"          # normally set outside Python; here for the demo
os.environ["SHOP_BATCH_SIZE"] = "500"

print(os.environ["SHOP_DB_HOST"])
print(os.getenv("SHOP_DB_PORT", "5432"))          # default when it's not set
print(os.getenv("SHOP_DB_PORT"))                  # None when not set and no default
print(type(os.environ["SHOP_BATCH_SIZE"]))        # always a str!
```

```text
localhost
5432
None
<class 'str'>
```

Environment values are **always strings**, so convert them, and fail clearly when a required one
is missing:

```python
class ConfigError(RuntimeError):
    pass

def env(name, default=None, cast=str, required=False):
    raw = os.environ.get(name)
    if raw is None or raw == "":
        if required:
            raise ConfigError(f"environment variable {name} is required but not set")
        return default
    if cast is bool:
        return raw.strip().lower() in {"1", "true", "yes", "on"}
    return cast(raw)

batch_size = env("SHOP_BATCH_SIZE", 100, cast=int)
dry_run = env("SHOP_DRY_RUN", False, cast=bool)
print(batch_size, type(batch_size).__name__, dry_run)
try:
    env("SHOP_DB_PASSWORD", required=True)
except ConfigError as e:
    print("ConfigError:", e)
```

```text
500 int False
ConfigError: environment variable SHOP_DB_PASSWORD is required but not set
```

Failing at **start-up** with a clear message beats failing an hour into a run with
`authentication failed`.

## .env files with python-dotenv

Typing `export` for ten variables gets old. A `.env` file holds them for local development, and
`load_dotenv()` copies them into `os.environ`:

```python
from pathlib import Path
from dotenv import load_dotenv

Path("output").mkdir(exist_ok=True)
Path("output/.env").write_text(
    "# local development settings: NEVER commit this file\n"
    "SHOP_DB_USER=shop_app\n"
    "SHOP_DB_PASSWORD=dev-only-password\n"
    "SHOP_API_TOKEN=abc123\n"
    "SHOP_DB_HOST=db.internal\n"
)

load_dotenv("output/.env")                    # does NOT overwrite variables already set
print(os.environ["SHOP_DB_USER"], os.environ["SHOP_DB_HOST"])
```

```text
shop_app localhost
```

`SHOP_DB_HOST` stayed `localhost`: by default **real environment variables win** over the `.env`
file, so production settings can't be silently replaced by a forgotten local file
(`load_dotenv(override=True)` changes that).

The rules for `.env`:

1. Add `.env` to `.gitignore`, **before** your first commit.
2. Commit a `.env.example` with the variable **names** and empty values, so teammates know what to set.
3. On servers, set real environment variables (or use a secrets manager); `.env` is for your laptop.

## Config files

### INI with configparser (built in)

```python
import configparser

Path("output/pipeline.ini").write_text("""
[source]
orders_path = data/orders.csv
delimiter = ,

[load]
batch_size = 500
dry_run = false
""")

cfg = configparser.ConfigParser()
cfg.read("output/pipeline.ini")
print(cfg["source"]["orders_path"])
print(cfg.getint("load", "batch_size"), cfg.getboolean("load", "dry_run"))
```

```text
data/orders.csv
500 False
```

### JSON

```python
import json

Path("output/pipeline.json").write_text(json.dumps(
    {"source": {"orders_path": "data/orders.csv"}, "load": {"batch_size": 500, "tables": ["orders", "customers"]}},
    indent=2))
cfg = json.loads(Path("output/pipeline.json").read_text())
print(cfg["load"]["tables"], cfg["load"]["batch_size"] + 1)
```

```text
['orders', 'customers'] 501
```

JSON is strict (no comments, no trailing commas), so it's better for machines than for people.

### YAML

YAML is the most common format in data tools (Airflow, dbt, Docker Compose, GitHub Actions):

```python
import yaml

Path("output/pipeline.yaml").write_text("""
# daily orders pipeline
source:
  orders_path: data/orders.csv
load:
  batch_size: 500
  tables: [orders, customers]
  schedule: "0 6 * * *"     # 6 AM daily, quoted so YAML keeps it as text
""")

cfg = yaml.safe_load(Path("output/pipeline.yaml").read_text())
print(cfg["load"]["tables"], cfg["load"]["batch_size"], repr(cfg["load"]["schedule"]))
```

```text
['orders', 'customers'] 500 '0 6 * * *'
```

:::{warning}
Always use **`yaml.safe_load`**. Plain `yaml.load` can be tricked into running code by a malicious
file.
:::

### TOML

TOML is clear and typed, and Python 3.11+ reads it with the built-in `tomllib` (`pyproject.toml` is
TOML). Use the `try` import so the code also works on older Pythons, with `pip install tomli`:

```python
try:
    import tomllib                    # Python 3.11+
except ImportError:
    import tomli as tomllib           # older Python: pip install tomli

Path("output/pipeline.toml").write_text("""
[source]
orders_path = "data/orders.csv"

[load]
batch_size = 500
dry_run = false
tables = ["orders", "customers"]
""")

with open("output/pipeline.toml", "rb") as f:     # tomllib needs binary mode
    cfg = tomllib.load(f)
print(cfg["load"])
```

```text
{'batch_size': 500, 'dry_run': False, 'tables': ['orders', 'customers']}
```

| Format | Built in? | Comments | Types | Typical home |
|---|---|---|---|---|
| INI | yes | yes | text only (you convert) | older tools, simple settings |
| JSON | yes | no | yes | machine-generated config, APIs |
| YAML | `pyyaml` | yes | yes | Airflow, dbt, Docker, GitHub Actions |
| TOML | 3.11+ | yes | yes | `pyproject.toml`, modern Python apps |

## Putting it together: layered settings

The usual order, from weakest to strongest: **defaults in code → config file → environment
variables**. So a file sets the normal values and the environment overrides per machine:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    orders_path: str
    batch_size: int
    dry_run: bool
    db_password: str

def load_settings(config_path="output/pipeline.toml"):
    with open(config_path, "rb") as f:
        file_cfg = tomllib.load(f)
    return Settings(
        orders_path=file_cfg["source"]["orders_path"],
        batch_size=env("SHOP_BATCH_SIZE", file_cfg["load"]["batch_size"], cast=int),  # env overrides file
        dry_run=env("SHOP_DRY_RUN", file_cfg["load"]["dry_run"], cast=bool),
        db_password=env("SHOP_DB_PASSWORD", required=True),                             # secrets: env only
    )

os.environ["SHOP_BATCH_SIZE"] = "1000"
settings = load_settings()
print(settings.orders_path, settings.batch_size, settings.dry_run)
print(f"password: {'*' * 8}")                     # never log secrets, even in debug output
```

```text
data/orders.csv 1000 False
password: ********
```

`SHOP_DB_PASSWORD` came from the `.env` file loaded earlier. The `frozen=True` dataclass means
settings can't be changed by accident halfway through a run, and every setting has one clear name
and type.

## Common mistakes

- **Secrets in code or Git.** Once pushed, assume the secret is leaked: revoke it and make a new one.
  Deleting the commit isn't enough.
- **Forgetting that env values are strings.** `if os.getenv("DRY_RUN"):` is true even for `"false"`!
- **Missing settings failing late.** Check required settings at start-up.
- **`yaml.load` instead of `yaml.safe_load`.**
- **Printing the whole settings object** in logs when it contains a password.

## Hands-on exercises

**Exercise 1 · Required with a hint.** Make `env()` include a hint in the error: *"set it in .env or
export it"*. Trigger it with `SHOP_S3_BUCKET`.

<details class="solution"><summary>Solution</summary>

```python
def env_required(name):
    value = os.environ.get(name)
    if not value:
        raise ConfigError(f"{name} is not set: add it to .env or export it in your shell")
    return value

try:
    env_required("SHOP_S3_BUCKET")
except ConfigError as e:
    print(e)
```

```text
SHOP_S3_BUCKET is not set: add it to .env or export it in your shell
```

</details>

**Exercise 2 · A .env.example.** Write `output/.env.example` listing every variable name from
`output/.env` with an **empty** value, keeping the comment lines.

<details class="solution"><summary>Solution</summary>

```python
lines = []
for line in Path("output/.env").read_text().splitlines():
    if line.startswith("#") or "=" not in line:
        lines.append(line)
    else:
        lines.append(line.split("=", 1)[0] + "=")
Path("output/.env.example").write_text("\n".join(lines) + "\n")
print(Path("output/.env.example").read_text(), end="")
```

```text
# local development settings: NEVER commit this file
SHOP_DB_USER=
SHOP_DB_PASSWORD=
SHOP_API_TOKEN=
SHOP_DB_HOST=
```

</details>

**Exercise 3 · Per-environment YAML.** Write a YAML file with `dev:` and `prod:` sections (different
`batch_size`), and pick the section using an `APP_ENV` environment variable (default `dev`).

<details class="solution"><summary>Solution</summary>

```python
Path("output/envs.yaml").write_text("""
dev:  {batch_size: 50, output: output/dev}
prod: {batch_size: 5000, output: s3://shop-lake/prod}
""")
all_cfg = yaml.safe_load(Path("output/envs.yaml").read_text())
os.environ["APP_ENV"] = "prod"
cfg = all_cfg[os.getenv("APP_ENV", "dev")]
print(cfg)
```

```text
{'batch_size': 5000, 'output': 's3://shop-lake/prod'}
```

</details>

**Exercise 4 · Bool trap.** Show that `bool(os.getenv("SHOP_DRY_RUN"))` is `True` when the variable is
`"false"`, then fix it with the `env()` helper.

<details class="solution"><summary>Solution</summary>

```python
os.environ["SHOP_DRY_RUN"] = "false"
print(bool(os.getenv("SHOP_DRY_RUN")), env("SHOP_DRY_RUN", cast=bool))
```

```text
True False
```

</details>

**Exercise 5 · Mask secrets in a printout.** Write `safe_repr(settings)` that prints every field but
replaces any field whose name contains `password`, `token` or `secret` with `***`.

<details class="solution"><summary>Solution</summary>

```python
from dataclasses import asdict

def safe_repr(obj):
    hidden = ("password", "token", "secret")
    return {k: ("***" if any(h in k for h in hidden) else v) for k, v in asdict(obj).items()}

print(safe_repr(settings))
```

```text
{'orders_path': 'data/orders.csv', 'batch_size': 1000, 'dry_run': False, 'db_password': '***'}
```

</details>
