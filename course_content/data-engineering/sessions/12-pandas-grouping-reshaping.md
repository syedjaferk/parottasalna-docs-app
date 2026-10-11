# Session 12 · Pandas: grouping, joining, pivoting and reshaping

## The big idea

Raw data is a long list of events. Reports and warehouse tables need **summaries** ("revenue per
city per month") and **shapes** that suit the next tool. Pandas covers both:

- **groupby**: split rows into groups, calculate something for each group, combine the results.
- **merge**: join two tables on a key (SQL's `JOIN`).
- **pivot / melt / stack**: turn long tables wide and wide tables long.

We finish by putting the whole module together in a small **ETL pipeline** that writes Parquet,
partitioned by month.

**Everyday example:** a shop owner's notebook lists every sale (long). At month end they draw a grid
with cities down the side and months across the top (wide). Same data, different shape.

Run the examples in order. We start from the cleaning steps of Session 11:

```python
import json
import pandas as pd

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", None)

orders = (
    pd.read_csv("data/orders.csv", parse_dates=["order_date"])
      .drop_duplicates(subset="order_id")
      .assign(city=lambda d: d["city"].fillna("UNKNOWN"),
              amount=lambda d: d["quantity"] * d["unit_price"],
              month=lambda d: d["order_date"].dt.strftime("%Y-%m"))
)
delivered = orders[orders["status"] == "delivered"]
print(len(orders), len(delivered))
```

```text
12 10
```

`assign` adds columns inside a **method chain**. Each line is one clear step, read top to bottom.

## groupby: split → apply → combine

```{raw} html
:file: ../diagrams/s12-groupby.html
```

```python
print(delivered.groupby("city")["amount"].sum().sort_values(ascending=False))
```

```text
city
Chennai       65000
Madurai       52400
Coimbatore     2400
Trichy          750
Salem           200
UNKNOWN         200
Name: amount, dtype: int64
```

### Several numbers per group: named aggregations

```python
summary = (
    delivered.groupby("category")
             .agg(orders=("order_id", "count"),
                  units=("quantity", "sum"),
                  revenue=("amount", "sum"),
                  avg_order=("amount", "mean"),
                  biggest=("amount", "max"))
             .round(2)
             .sort_values("revenue", ascending=False)
)
print(summary)
```

```text
             orders  units  revenue  avg_order  biggest
category                                              
Electronics       5      6   118900    23780.0    55000
Stationery        4     85     1300      325.0      500
Home              1      3      750      750.0      750
```

### Grouping by two columns

```python
by_city_month = delivered.groupby(["city", "month"], as_index=False)["amount"].sum()
print(by_city_month)
```

```text
         city    month  amount
0     Chennai  2025-01   55000
1     Chennai  2025-02   10000
2  Coimbatore  2025-01    2400
3     Madurai  2025-01     400
4     Madurai  2025-02   52000
5       Salem  2025-02     200
6      Trichy  2025-01     750
7     UNKNOWN  2025-01     200
```

`as_index=False` keeps the group keys as normal columns: the shape a database table expects.

### transform: a group value on every row

`agg` returns one row per group; `transform` returns one value **per original row**. That's how you
compute "share of the city's revenue" without a separate join:

```python
d = delivered[["order_id", "city", "amount"]].copy()
d["city_total"] = d.groupby("city")["amount"].transform("sum")
d["share_pct"] = (100 * d["amount"] / d["city_total"]).round(1)
print(d[d["city"] == "Chennai"].to_string(index=False))
```

```text
 order_id    city  amount  city_total  share_pct
     1001 Chennai   55000       65000       84.6
     1011 Chennai    9500       65000       14.6
     1012 Chennai     500       65000        0.8
```

## merge: joining tables

Orders only have `customer_id`. To report by customer name, **join** to the customers table:

```python
with open("data/customers.json") as f:
    customers = pd.json_normalize(json.load(f))[["customer_id", "name", "address.city"]]
customers = customers.rename(columns={"address.city": "home_city"})

enriched = delivered.merge(customers, on="customer_id", how="left", validate="many_to_one", indicator=True)
print(enriched["_merge"].value_counts().to_dict())
print(enriched.groupby("name")["amount"].sum().sort_values(ascending=False).head(3))
```

```text
{'both': 10, 'left_only': 0, 'right_only': 0}
name
Arun       55500
Karthik    52400
Ravi        9500
Name: amount, dtype: int64
```

- `how="left"` keeps every order even without a matching customer (`"inner"` would silently drop them).
- `validate="many_to_one"` raises an error if a customer ID appears twice in `customers`. Without it,
  a duplicated customer would quietly **double** the matching orders.
- `indicator=True` adds `_merge`, so you can count unmatched rows. Check it after every join.

## pivot_table: long → wide

```python
report = delivered.pivot_table(index="city", columns="month", values="amount",
                               aggfunc="sum", fill_value=0, margins=True, margins_name="Total")
print(report)
```

```text
month       2025-01  2025-02   Total
city                                
Chennai       55000    10000   65000
Coimbatore     2400        0    2400
Madurai         400    52000   52400
Salem             0      200     200
Trichy          750        0     750
UNKNOWN         200        0     200
Total         58750    62200  120950
```

`pivot_table` aggregates when several rows land in the same cell. Plain `pivot` doesn't; it raises an
error on duplicates, which is useful when duplicates would mean a bug.

`pd.crosstab` is a shortcut for **counting**:

```python
print(pd.crosstab(orders["category"], orders["status"]))
```

```text
status       cancelled  delivered  returned
category                                   
Electronics          0          5         1
Home                 1          1         0
Stationery           0          4         0
```

## melt and stack: wide → long

Spreadsheets arrive wide (one column per week). Most tools want **long** data: one row per
measurement. `melt` unpivots:

```python
weekly = pd.DataFrame({"city": ["Chennai", "Coimbatore"],
                       "week_1": [12000, 4000], "week_2": [15000, 3500], "week_3": [11000, 5000]})
long = weekly.melt(id_vars="city", var_name="week", value_name="sales")
print(long)
print(long.pivot(index="city", columns="week", values="sales"))    # and back again
```

```text
         city    week  sales
0     Chennai  week_1  12000
1  Coimbatore  week_1   4000
2     Chennai  week_2  15000
3  Coimbatore  week_2   3500
4     Chennai  week_3  11000
5  Coimbatore  week_3   5000
week        week_1  week_2  week_3
city                              
Chennai      12000   15000   11000
Coimbatore    4000    3500    5000
```

`stack` and `unstack` do the same with the index: `unstack` moves an index level into columns,
`stack` moves columns into the index:

```python
s = delivered.groupby(["category", "month"])["amount"].sum()
wide = s.unstack(fill_value=0)
print(wide)
print(wide.stack().head(3))
```

```text
month        2025-01  2025-02
category                     
Electronics    57400    61500
Home             750        0
Stationery       600      700
category     month  
Electronics  2025-01    57400
             2025-02    61500
Home         2025-01      750
dtype: int64
```

| Shape | Good for |
|---|---|
| **long** (tidy): one row per fact | databases, Spark, plotting libraries, appending new data |
| **wide**: one column per category or period | human reports, spreadsheets, side-by-side comparison |

## Putting it all together: a mini ETL pipeline

Everything from Module 1 in one script: config, logging, functions, file formats, cleaning, grouping,
and partitioned Parquet output, the layout Spark and Databricks read natively.

```python
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s", stream=sys.stdout, force=True)
log = logging.getLogger("orders_etl")

CONFIG = {"orders": "data/orders.csv", "customers": "data/customers.json", "out": "output/lake"}

def extract(cfg):
    orders = pd.read_csv(cfg["orders"], parse_dates=["order_date"])
    with open(cfg["customers"]) as f:
        customers = pd.json_normalize(json.load(f))
    log.info("extracted %d orders, %d customers", len(orders), len(customers))
    return orders, customers

def transform(orders, customers):
    before = len(orders)
    orders = orders.drop_duplicates(subset="order_id")
    if before != len(orders):
        log.warning("dropped %d duplicate order(s)", before - len(orders))
    missing_city = orders["city"].isna().sum()
    if missing_city:
        log.warning("%d order(s) without a city; using the customer's home city", missing_city)
    facts = (
        orders.merge(customers[["customer_id", "name", "address.city"]], on="customer_id",
                     how="left", validate="many_to_one")
              .assign(city=lambda d: d["city"].fillna(d["address.city"]),
                      amount=lambda d: d["quantity"] * d["unit_price"],
                      month=lambda d: d["order_date"].dt.strftime("%Y-%m"))
              .query("status == 'delivered'")
              .drop(columns=["address.city"])
    )
    assert facts["amount"].ge(0).all(), "negative amounts found"
    return facts

def load(facts, out):
    facts.to_parquet(out, partition_cols=["month"], index=False)      # one folder per month
    log.info("loaded %d rows into %s", len(facts), out)

orders_raw, customers_raw = extract(CONFIG)
facts = transform(orders_raw, customers_raw)
load(facts, CONFIG["out"])

for path in sorted(Path(CONFIG["out"]).rglob("*.parquet")):
    print(path.parent.name)
back = pd.read_parquet(CONFIG["out"], filters=[("month", "=", "2025-02")])
print(len(back), back["amount"].sum())
```

```text
INFO orders_etl: extracted 13 orders, 6 customers
WARNING orders_etl: dropped 1 duplicate order(s)
WARNING orders_etl: 1 order(s) without a city; using the customer's home city
INFO orders_etl: loaded 10 rows into output/lake
month=2025-01
month=2025-02
4 62200
```

Order 1005's missing city was filled from the customer's home city (Salem), a better fix than
`"UNKNOWN"`. And reading `month=2025-02` with `filters` touched **only that folder**: on terabytes
of data, that's the difference between seconds and hours. You'll build this same pipeline with
Airflow (Module 5) and on Databricks with Delta Lake (Module 7).

## Common mistakes

- **Joining without checking**: no `validate=`, no look at unmatched rows. Duplicated keys silently
  multiply rows.
- **`count` vs `size`**: `count` skips missing values; `size` counts rows.
- **Forgetting `as_index=False` / `reset_index()`** before saving a grouped result: the keys end up in
  the index, not in columns.
- **`pivot` with duplicates** raises *"Index contains duplicate entries"*. Use `pivot_table` with an
  `aggfunc`, or fix the duplicates.
- **Wide tables in a database.** A new month means a new column. Store long; pivot only for reports.

## Hands-on exercises

**Exercise 1 · Best product per category.** For delivered orders, find the product with the highest
revenue in each category.

<details class="solution"><summary>Solution</summary>

```python
rev = delivered.groupby(["category", "product"], as_index=False)["amount"].sum()
best = rev.loc[rev.groupby("category")["amount"].idxmax()]
print(best.to_string(index=False))
```

```text
   category      product  amount
Electronics       Laptop  107000
       Home Water Bottle     750
 Stationery          Pen     700
```

</details>

**Exercise 2 · Monthly growth.** Compute total delivered revenue per month and the growth from
January to February in percent.

<details class="solution"><summary>Solution</summary>

```python
monthly = delivered.groupby("month")["amount"].sum()
print(monthly.to_dict())
print(f"growth: {monthly.pct_change().iloc[-1] * 100:.1f}%")
```

```text
{'2025-01': 58750, '2025-02': 62200}
growth: 5.9%
```

</details>

**Exercise 3 · Customers' first order.** For each customer, show the date of their first order and how
many orders they placed (any status).

<details class="solution"><summary>Solution</summary>

```python
first = (orders.groupby("customer_id")
               .agg(first_order=("order_date", "min"), orders=("order_id", "count"))
               .reset_index())
print(first.to_string(index=False))
```

```text
customer_id first_order  orders
        C01  2025-01-03       3
        C02  2025-01-03       2
        C03  2025-01-04       2
        C04  2025-01-05       2
        C05  2025-01-06       2
        C06  2025-01-08       1
```

</details>

**Exercise 4 · Status counts per city, wide.** Make a table with cities as rows, statuses as columns
and order counts as values (0 where none).

<details class="solution"><summary>Solution</summary>

```python
print(orders.pivot_table(index="city", columns="status", values="order_id", aggfunc="count", fill_value=0))
```

```text
status      cancelled  delivered  returned
city                                      
Chennai             1          3         1
Coimbatore          0          2         0
Madurai             0          2         0
Salem               0          1         0
Trichy              0          1         0
UNKNOWN             0          1         0
```

</details>

**Exercise 5 · Unpivot a report.** Take `report` (the city × month pivot, with totals), drop the
`Total` row and column, and melt it back to a long table of non-zero values.

<details class="solution"><summary>Solution</summary>

```python
long_report = (report.drop(index="Total", columns="Total")
                     .reset_index()
                     .melt(id_vars="city", var_name="month", value_name="amount")
                     .query("amount > 0")
                     .sort_values(["city", "month"]))
print(long_report.to_string(index=False))
```

```text
      city   month  amount
   Chennai 2025-01   55000
   Chennai 2025-02   10000
Coimbatore 2025-01    2400
   Madurai 2025-01     400
   Madurai 2025-02   52000
     Salem 2025-02     200
    Trichy 2025-01     750
   UNKNOWN 2025-01     200
```

Same numbers as `by_city_month` earlier: long → wide → long loses nothing.

</details>

**Exercise 6 · Extend the pipeline.** Add a `validate(facts)` step to the ETL that logs an ERROR and
raises if any `order_id` is duplicated or any `amount` is missing. Run it on `facts`.

<details class="solution"><summary>Solution</summary>

```python
def validate(facts):
    problems = []
    if facts["order_id"].duplicated().any():
        problems.append("duplicate order_id")
    if facts["amount"].isna().any():
        problems.append("missing amount")
    if problems:
        log.error("validation failed: %s", ", ".join(problems))
        raise ValueError(problems)
    log.info("validation passed for %d rows", len(facts))

validate(facts)
```

```text
INFO orders_etl: validation passed for 10 rows
```

That's a data-quality check, the idea behind Great Expectations and dbt tests in Module 4.

</details>
