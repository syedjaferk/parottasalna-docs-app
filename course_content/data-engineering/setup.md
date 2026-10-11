# Setup

Do this once before Session 1. About 15 minutes.

## 1 · Python 3.11 or newer

Check what you have:

```bash
python3 --version
```

If it's older than 3.11, install the latest from [python.org](https://www.python.org/downloads/)
(on Windows tick **Add Python to PATH**). Python 3.11 adds `tomllib` for reading TOML config files,
which we use in Session 9.

## 2 · A project folder and a virtual environment

```bash
mkdir data-engineering && cd data-engineering
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

Your prompt now starts with `(.venv)`. Activate it every time you open a new terminal.

## 3 · Install the libraries for Module 1

```bash
pip install pandas numpy pyarrow requests python-dotenv pyyaml jupyterlab
```

| Library | Used for | Session |
|---|---|---|
| `requests` | calling REST APIs | 8 |
| `python-dotenv`, `pyyaml` | `.env` files and YAML config | 9 |
| `numpy` | fast arrays and maths | 10 |
| `pandas` | tables: cleaning, grouping, reshaping | 11–12 |
| `pyarrow` | reading and writing **Parquet** files | 7, 12 |
| `jupyterlab` | optional: notebooks for experimenting | any |

## 4 · Download the practice dataset

Every session uses the same small **shop dataset**. Make a `data` folder inside your project and
save these four files into it:

| File | What's inside |
|---|---|
| {download}`orders.csv <code/data/orders.csv>` | 13 orders, with a few real-world problems (a missing city, a duplicate row, cancelled and returned orders) |
| {download}`customers.json <code/data/customers.json>` | 6 customers with nested addresses and tags |
| {download}`events.jsonl <code/data/events.jsonl>` | website click events, one JSON object per line (and one broken line, on purpose) |
| {download}`server.log <code/data/server.log>` | a short pipeline log |

Your folder should look like this:

```text
data-engineering/
├── .venv/
└── data/
    ├── customers.json
    ├── events.jsonl
    ├── orders.csv
    └── server.log
```

Run the examples from the `data-engineering` folder, so paths like `data/orders.csv` work.

## Check everything works

```bash
python -c "import pandas, numpy, pyarrow, requests; print('ready')"
```
