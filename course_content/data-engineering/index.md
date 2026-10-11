# End-to-End Data Engineering

Build modern data pipelines from scratch: Python, SQL, data modelling, ETL/ELT, Airflow, PySpark,
Databricks (with Certified Data Engineer Associate prep), streaming and CI/CD, finishing with
capstone projects.

:::{note}
**How to use these notes.** Each session page matches one live class (Mon, Wed, Fri · 8–9 PM IST).
Read the page after class, run every example yourself, then do the **hands-on exercises**:
solutions are hidden until you click. Each session also has a quiz and flashcards, linked at the
bottom of the page.
:::

## The course at a glance

| # | Module | Status |
|---|---|---|
| 1 | **Python for Data Engineering** (foundation) | ✅ available below |
| 2 | SQL for Data Engineering | coming soon |
| 3 | Data Modeling & Warehousing | coming soon |
| 4 | Data Pipelines & ETL/ELT (with dbt) | coming soon |
| 5 | Apache Airflow | coming soon |
| 6 | PySpark & Big Data Processing | coming soon |
| 7 | Databricks + certification prep | coming soon |
| 8 | Streaming & Real-Time Data | coming soon |
| 9 | Infrastructure, Version Control & CI/CD | coming soon |
| 10 | Capstone projects | coming soon |

See the full syllabus at [dataengineering.parottasalna.com](https://dataengineering.parottasalna.com/).

## Module 1 · Python for Data Engineering

Data engineers write Python every day to **move and shape data**: read files and APIs, clean
records, handle failures, and hand tidy tables to the next step. This module teaches exactly that
Python, using one small **shop dataset** (orders, customers, click events and a log file) that we
keep reusing, so by the end you'll have built a tiny ETL pipeline.

| Part | Sessions | You'll be able to… |
|---|---|---|
| A · Core Python | 1–4 | write clear scripts that read input, make decisions, reuse logic and fail safely with good logs |
| B · Data Structures | 5–6 | hold records in the right structure and stream large data without running out of memory |
| C · Files & APIs | 7–9 | read and write CSV, JSON and Parquet, pull data from REST APIs, and keep secrets out of code |
| D · Libraries | 10–12 | crunch numbers with NumPy and clean, group and reshape tables with Pandas |

```{toctree}
:maxdepth: 1
:caption: Getting started

setup
```

```{toctree}
:maxdepth: 1
:caption: Part A · Core Python

sessions/01-data-types-variables-io
sessions/02-control-flow-and-loops
sessions/03-functions-scope-lambda
sessions/04-exceptions-and-logging
```

```{toctree}
:maxdepth: 1
:caption: Part B · Data Structures

sessions/05-lists-tuples-dicts-sets
sessions/06-comprehensions-and-generators
```

```{toctree}
:maxdepth: 1
:caption: Part C · Files & APIs

sessions/07-files-text-csv-json-parquet
sessions/08-rest-apis-with-requests
sessions/09-environment-and-config
```

```{toctree}
:maxdepth: 1
:caption: Part D · Essential Libraries

sessions/10-numpy
sessions/11-pandas-series-dataframes
sessions/12-pandas-grouping-reshaping
```
