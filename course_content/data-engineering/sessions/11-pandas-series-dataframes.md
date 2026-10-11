# Session 11 · Pandas: Series, DataFrames and indexing

## The big idea

Pandas gives Python a **table**: the DataFrame. It's what you reach for to load a CSV, look at it,
fix it and hand it on. Under the hood every column is a NumPy array (Session 10), so operations on
whole columns are fast, but each column can have its own type and every row has a label (the
**index**).

**Everyday example:** a DataFrame is a spreadsheet you control with code. Every step is written
down, repeatable, and works the same on 13 rows or 13 million.

Run the examples in order (`import pandas as pd` is the universal convention).

```{raw} html
:file: ../diagrams/s11-dataframe.html
```

## Series: one labelled column

```python
import pandas as pd

stock = pd.Series({"Laptop": 4, "Mouse": 30, "Pen": 500})
print(stock)
print(stock["Mouse"], stock.index.tolist(), stock.values)
```

```text
Laptop      4
Mouse      30
Pen       500
dtype: int64
30 ['Laptop', 'Mouse', 'Pen'] [  4  30 500]
```

Operations between Series **line up by label**, not by position. That's powerful, and
occasionally surprising:

```python
sold = pd.Series({"Pen": 70, "Laptop": 1, "Notebook": 15})
print(stock - sold)
```

```text
Laptop        3.0
Mouse         NaN
Notebook      NaN
Pen         430.0
dtype: float64
```

`Mouse` and `Notebook` appear in only one Series, so the result is `NaN` (missing). Use
`stock.sub(sold, fill_value=0)` to treat a missing side as 0.

## Loading a DataFrame

```python
pd.set_option("display.width", 120)          # print wide tables in full instead of "..."
pd.set_option("display.max_columns", None)
orders = pd.read_csv("data/orders.csv", parse_dates=["order_date"])
print(orders.shape)
print(orders.head(3))
print(orders.dtypes)
```

```text
(13, 9)
   order_id order_date customer_id        city   product     category  quantity  unit_price     status
0      1001 2025-01-03         C01     Chennai    Laptop  Electronics         1       55000  delivered
1      1002 2025-01-03         C02  Coimbatore     Mouse  Electronics         2         450  delivered
2      1003 2025-01-04         C03     Madurai  Notebook   Stationery        10          40  delivered
order_id                int64
order_date     datetime64[ns]
customer_id            object
city                   object
product                object
category               object
quantity                int64
unit_price              int64
status                 object
dtype: object
```

Unlike plain CSV reading, pandas **infers types**: numbers became `int64`, and `parse_dates` turned
the date text into real dates. Text columns show as `object`.

### A first look

```python
print(orders.describe().loc[["mean", "min", "max"], ["quantity", "unit_price"]])
print(orders["status"].value_counts())
print(orders.isna().sum()[lambda s: s > 0])     # columns with missing values
```

```text
       quantity    unit_price
mean   7.615385   9388.461538
min    1.000000     10.000000
max   50.000000  55000.000000
status
delivered    11
returned      1
cancelled     1
Name: count, dtype: int64
city    1
dtype: int64
```

Three lines tell you a lot: there's a missing city, and the price range is huge (₹10 to ₹55,000).

## Selecting columns

```python
print(orders["product"].head(3).tolist())               # one column → a Series
print(orders[["order_id", "product"]].head(2))          # list of columns → a DataFrame

orders["amount"] = orders["quantity"] * orders["unit_price"]     # new column, vectorised
orders = orders.rename(columns={"unit_price": "price"})
print(orders.columns.tolist())
```

```text
['Laptop', 'Mouse', 'Notebook']
   order_id product
0      1001  Laptop
1      1002   Mouse
['order_id', 'order_date', 'customer_id', 'city', 'product', 'category', 'quantity', 'price', 'status', 'amount']
```

## Selecting rows: filters, loc and iloc

A **boolean filter** works like NumPy masks (Session 10) and SQL's `WHERE`:

```python
delivered_electronics = orders[(orders["status"] == "delivered") & (orders["category"] == "Electronics")]
print(delivered_electronics[["order_id", "product", "amount"]])

print(orders[orders["city"].isin(["Madurai", "Salem"])]["order_id"].tolist())
print(orders.query("amount > 5000 and status == 'delivered'")["product"].tolist())
```

```text
    order_id   product  amount
0       1001    Laptop   55000
1       1002     Mouse     900
6       1007  Keyboard    1500
9       1009    Laptop   52000
11      1011   Monitor    9500
[1003, 1009, 1010]
['Laptop', 'Laptop', 'Monitor']
```

`loc` selects by **label**, `iloc` by **position**:

```python
by_id = orders.set_index("order_id")                     # use order_id as the row label
print(by_id.loc[1011, "product"], by_id.loc[1011, "amount"])   # one cell at a time, by label
print(by_id.loc[1002:1004, "product"].tolist())          # label slices INCLUDE the end
print(orders.iloc[0, 4], orders.iloc[-1]["product"])     # first row 5th column; last row
print(orders.iloc[2:4]["order_id"].tolist())             # position slices EXCLUDE the end
```

```text
Monitor 9500
['Mouse', 'Notebook', 'Headphones']
Laptop Pen
[1003, 1004]
```

| You want | Use |
|---|---|
| rows matching a condition | `df[condition]` or `df.loc[condition, columns]` |
| a row by its label (ID) | `df.loc[label]` |
| a row by its position | `df.iloc[n]` |
| change values in matching rows | `df.loc[condition, "col"] = value` |

## Cleaning: missing values, duplicates and types

```python
clean = orders.copy()                                        # never modify the raw data in place
clean["city"] = clean["city"].fillna("UNKNOWN")
print(clean["city"].isna().sum())

print(clean.duplicated(subset="order_id").sum(), "duplicate row(s)")
clean = clean.drop_duplicates(subset="order_id", keep="first")

clean["status"] = clean["status"].astype("category")         # few distinct values → category
clean.loc[clean["status"] != "delivered", "amount"] = 0      # no revenue for returns/cancellations
print(len(clean), clean["amount"].sum(), clean["status"].dtype)
```

```text
0
1 duplicate row(s)
12 120950 category
```

12 rows and ₹120,950: the same answer as the generator pipeline in Session 6, now in 6 lines.

### Dates

```python
clean["month"] = clean["order_date"].dt.to_period("M").astype(str)
clean["weekday"] = clean["order_date"].dt.day_name()
print(clean[["order_date", "month", "weekday"]].head(3))
print(clean[clean["order_date"].between("2025-02-01", "2025-02-28")]["order_id"].tolist())
```

```text
  order_date    month   weekday
0 2025-01-03  2025-01    Friday
1 2025-01-03  2025-01    Friday
2 2025-01-04  2025-01  Saturday
[1009, 1010, 1011, 1012]
```

## Sorting

```python
top = clean.sort_values(["amount", "order_id"], ascending=[False, True]).head(3)
print(top[["order_id", "product", "amount"]].to_string(index=False))
```

```text
 order_id product  amount
     1001  Laptop   55000
     1009  Laptop   52000
     1011 Monitor    9500
```

## Common mistakes

- **Chained assignment**: `df[df.city == "Chennai"]["amount"] = 0` may change a **copy** (pandas
  warns: *SettingWithCopyWarning*). Use `df.loc[df.city == "Chennai", "amount"] = 0`.
- **`and`/`or` in filters**: use `&`, `|`, `~` with brackets around each condition.
- **Forgetting `.copy()`** when you take a filtered piece you'll modify.
- **Mixing up `loc` and `iloc`**: label slices include the end, position slices don't.
- **Reading IDs as numbers.** Leading zeros vanish (`"007"` → `7`). Use `dtype={"pincode": str}` for
  codes and IDs.

## Hands-on exercises

**Exercise 1 · Load with types.** Read `orders.csv` so that `customer_id` and `order_id` are strings and
`order_date` is a date. Print the three dtypes.

<details class="solution"><summary>Solution</summary>

```python
df = pd.read_csv("data/orders.csv", dtype={"order_id": str, "customer_id": str}, parse_dates=["order_date"])
print(df[["order_id", "customer_id", "order_date"]].dtypes.tolist())
```

```text
[dtype('O'), dtype('O'), dtype('<M8[ns]')]
```

(`O` is object/text and `<M8[ns]` is pandas' internal name for datetime64.)

</details>

**Exercise 2 · Chennai's delivered orders.** From `clean`, list the products of delivered orders in
Chennai, sorted by amount (highest first).

<details class="solution"><summary>Solution</summary>

```python
mask = (clean["city"] == "Chennai") & (clean["status"] == "delivered")
print(clean.loc[mask].sort_values("amount", ascending=False)["product"].tolist())
```

```text
['Laptop', 'Monitor', 'Pen']
```

</details>

**Exercise 3 · Customers to a DataFrame.** Load `customers.json` with `pd.json_normalize`, so the nested
address becomes columns. Print the column names.

<details class="solution"><summary>Solution</summary>

```python
import json

with open("data/customers.json") as f:
    customers = pd.json_normalize(json.load(f))
print(customers.columns.tolist())
```

```text
['customer_id', 'name', 'email', 'signup_date', 'tags', 'address.city', 'address.pincode']
```

</details>

**Exercise 4 · Missing emails.** How many customers have no email? Fill them with
`"unknown@example.com"` and print Meena's row.

<details class="solution"><summary>Solution</summary>

```python
print(customers["email"].isna().sum())
customers["email"] = customers["email"].fillna("unknown@example.com")
print(customers.loc[customers["name"] == "Meena", ["name", "email"]].to_string(index=False))
```

```text
1
 name               email
Meena unknown@example.com
```

</details>

**Exercise 5 · Price bands.** Add a `band` column with `pd.cut`: below ₹500 `"low"`, ₹500–₹9,999
`"mid"`, ₹10,000 and above `"high"`, and count rows per band.

<details class="solution"><summary>Solution</summary>

```python
clean["band"] = pd.cut(clean["price"], bins=[0, 500, 10000, float("inf")],
                       labels=["low", "mid", "high"], right=False)
print(clean["band"].value_counts().sort_index())
```

```text
band
low     6
mid     4
high    2
Name: count, dtype: int64
```

</details>
