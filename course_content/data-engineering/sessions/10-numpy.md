# Session 10 · NumPy: arrays, slicing, broadcasting, vectorised maths

## The big idea

Python lists are flexible but slow for maths: each number is a separate Python object, and loops
run one item at a time. **NumPy arrays** store numbers of one type packed together in memory, and
run operations on **all of them at once**, in fast compiled code. Pandas, Spark's Python API and most
ML libraries are built on top of NumPy.

**Everyday example:** a list is a stack of separate receipts you add up one by one; a NumPy array is
a spreadsheet column you total with one formula.

Run the examples in order (`import numpy as np` is the universal convention).

## Creating arrays

```python
import numpy as np

quantity = np.array([1, 2, 10, 1, 20, 1, 1, 3, 1, 5, 1, 50])
unit_price = np.array([55000, 450, 40, 1800, 10, 1200, 1500, 250, 52000, 40, 9500, 10], dtype=float)

print(quantity.dtype, quantity.shape, quantity.ndim)
print(unit_price.dtype, unit_price[:4].tolist())
print(np.arange(1, 6), np.zeros(3), np.linspace(0, 1, 5))
```

```text
int64 (12,) 1
float64 [55000.0, 450.0, 40.0, 1800.0]
[1 2 3 4 5] [0. 0. 0.] [0.   0.25 0.5  0.75 1.  ]
```

Every element has the **same dtype**. Mix ints and floats and NumPy picks float; mix in a string and
everything becomes text, which is a common surprise.

## Vectorised operations: no loops

Arithmetic between arrays works **element by element**:

```python
amount = quantity * unit_price            # 12 multiplications, one line
print(amount)
print(amount.sum(), amount.mean().round(2), amount.max(), amount.argmax())
```

```text
[55000.   900.   400.  1800.   200.  1200.  1500.   750. 52000.   200.
  9500.   500.]
123950.0 10329.17 55000.0 0
```

`argmax()` gives the **position** of the largest value: index 0, the laptop.

How much faster than a Python loop? On a million values:

```py
import timeit

big_q = np.random.default_rng(0).integers(1, 10, 1_000_000)
big_p = np.random.default_rng(1).random(1_000_000) * 1000
print(timeit.timeit(lambda: [q * p for q, p in zip(big_q, big_p)], number=3))
print(timeit.timeit(lambda: big_q * big_p, number=3))
```

```text
0.62         ← Python loop
0.0047       ← NumPy: about 100× faster
```

(Times vary by computer; the gap doesn't.)

## Indexing, slicing and boolean masks

```python
print(amount[0], amount[-1], amount[2:5])

expensive = unit_price > 5000              # a boolean array: the "mask"
print(expensive)
print(amount[expensive])                   # keep only where the mask is True
print(amount[(quantity >= 5) & (unit_price < 100)])   # & = and, | = or; brackets are required
print(amount[[0, 8, 10]])                  # pick specific positions ("fancy indexing")
```

```text
55000.0 500.0 [ 400. 1800.  200.]
[ True False False False False False False False  True False  True False]
[55000. 52000.  9500.]
[400. 200. 200. 500.]
[55000. 52000.  9500.]
```

Masks are the NumPy way to say **WHERE**: you'll see the same idea in pandas filters and in SQL.

### Slices are views, not copies

```python
prices = np.array([100.0, 200.0, 300.0])
first_two = prices[:2]          # a VIEW into the same memory
first_two[0] = 999
print(prices)                   # the original changed!

safe = prices[:2].copy()        # an independent copy
safe[0] = 1
print(prices)
```

```text
[999. 200. 300.]
[999. 200. 300.]
```

This saves memory on big arrays, but surprises people. Use `.copy()` when you'll modify a slice.

## 2-D arrays: rows and columns

Sales per city (rows) per week (columns):

```python
cities = np.array(["Chennai", "Coimbatore", "Madurai"])
weekly_sales = np.array([
    [12000, 15000, 11000, 18000],
    [ 4000,  3500,  5000,  4500],
    [ 7000,  6500,  8000,  9000],
])
print(weekly_sales.shape)
print(weekly_sales[1])            # row 1: Coimbatore, all weeks
print(weekly_sales[:, 3])         # column 3: week 4, all cities
print(weekly_sales[0, 2])         # Chennai, week 3
print(weekly_sales.sum(axis=1))   # total per city (across columns)
print(weekly_sales.sum(axis=0))   # total per week (down the rows)
print(cities[weekly_sales.sum(axis=1).argmax()])
```

```text
(3, 4)
[4000 3500 5000 4500]
[18000  4500  9000]
11000
[56000 17000 30500]
[23000 25000 24000 31500]
Chennai
```

`axis=0` means *collapse the rows* (one result per column); `axis=1` means *collapse the columns*
(one result per row).

## Broadcasting

When shapes differ, NumPy **stretches** the smaller one to fit, without copying data, if the shapes
are compatible: comparing from the right, each pair of sizes must be equal, or one of them must be 1.

```{raw} html
:file: ../diagrams/s10-broadcast.html
```

```python
print(weekly_sales * 1.18)                              # scalar: GST added to every cell

city_target = np.array([[15000], [4000], [8000]])       # shape (3, 1): one target per city
print(weekly_sales - city_target)                       # stretched across the 4 weeks

week_weight = np.array([1.0, 1.0, 0.5, 1.0])            # shape (4,): week 3 counts half
print(weekly_sales * week_weight)                       # stretched down the 3 rows
```

```text
[[14160. 17700. 12980. 21240.]
 [ 4720.  4130.  5900.  5310.]
 [ 8260.  7670.  9440. 10620.]]
[[-3000     0 -4000  3000]
 [    0  -500  1000   500]
 [-1000 -1500     0  1000]]
[[12000. 15000.  5500. 18000.]
 [ 4000.  3500.  2500.  4500.]
 [ 7000.  6500.  4000.  9000.]]
```

A classic use is **normalising** each city's sales to percentages of its own total:

```python
share = weekly_sales / weekly_sales.sum(axis=1, keepdims=True)   # (3,4) / (3,1)
print((share * 100).round(1))
```

```text
[[21.4 26.8 19.6 32.1]
 [23.5 20.6 29.4 26.5]
 [23.  21.3 26.2 29.5]]
```

`keepdims=True` keeps the result as shape `(3, 1)` instead of `(3,)`, so it lines up by row.

## Handy functions for data work

```python
status = np.array(["delivered", "delivered", "returned", "delivered", "cancelled", "delivered"])
values = np.array([55000, 900, 1800, 400, 1200, np.nan])            # nan = missing number

print(np.where(status == "delivered", values, 0))                   # vectorised if/else
print(np.clip(np.array([-5, 3, 120]), 0, 100))                      # limit to a range
print(np.unique(status, return_counts=True))
print(np.mean(values), np.nanmean(values))                          # nan spoils mean; nanmean skips it
print(np.isnan(values).sum(), "missing")
print(np.percentile(np.array([400, 900, 1200, 1800, 55000]), 50))  # the median
```

```text
[55000.   900.     0.   400.     0.    nan]
[  0   3 100]
(array(['cancelled', 'delivered', 'returned'], dtype='<U9'), array([1, 4, 1]))
nan 11860.0
1 missing
1200.0
```

### Synthetic data for testing

Pipelines need test data. A seeded random generator gives the same "random" data every run:

```python
rng = np.random.default_rng(42)
fake_quantities = rng.integers(1, 6, size=8)
fake_prices = rng.normal(loc=1000, scale=200, size=8).round(2)
print(fake_quantities)
print(fake_prices)
```

```text
[1 4 4 3 3 5 1 4]
[ 609.79  739.56 1025.57  936.75  996.64  829.39 1175.88 1155.56]
```

## Common mistakes

- **`and` / `or` with arrays** raises *"truth value of an array is ambiguous"*. Use `&`, `|`, `~`
  with brackets: `(a > 1) & (b < 5)`.
- **Changing a slice** and accidentally changing the original. Use `.copy()`.
- **Shape mismatches.** Shapes `(3, 4)` and `(3,)` don't broadcast; reshape to `(3, 1)` or use
  `keepdims=True`.
- **Integer overflow.** `int32` arrays wrap around silently beyond about 2.1 billion. Use `int64`
  for IDs and money in paise.
- **`np.nan == np.nan` is False.** Test with `np.isnan()`.

## Hands-on exercises

**Exercise 1 · Discount the electronics.** Give a 10 % discount to items with a unit price of
₹1,000 or more, and print the new total of `quantity * unit_price`.

<details class="solution"><summary>Solution</summary>

```python
discounted = np.where(unit_price >= 1000, unit_price * 0.9, unit_price)
print((quantity * discounted).sum())
```

```text
111850.0
```

</details>

**Exercise 2 · Best week per city.** For each city, print the week number (1–4) with its highest
sales.

<details class="solution"><summary>Solution</summary>

```python
for city, week in zip(cities, weekly_sales.argmax(axis=1) + 1):
    print(city, week)
```

```text
Chennai 4
Coimbatore 3
Madurai 4
```

</details>

**Exercise 3 · Week-on-week change.** Compute each city's change from the previous week (3 values
per city) with slicing, no loops.

<details class="solution"><summary>Solution</summary>

```python
print(weekly_sales[:, 1:] - weekly_sales[:, :-1])
```

```text
[[ 3000 -4000  7000]
 [ -500  1500  -500]
 [ -500  1500  1000]]
```

(`np.diff(weekly_sales, axis=1)` gives the same result.)

</details>

**Exercise 4 · Z-scores.** Standardise `amount`: subtract the mean and divide by the standard
deviation. Which positions have |z| > 2 (possible outliers)?

<details class="solution"><summary>Solution</summary>

```python
z = (amount - amount.mean()) / amount.std()
print(np.where(np.abs(z) > 2)[0])
```

```text
[0 8]
```

The two laptop orders (₹55,000 and ₹52,000) stand far above the rest. Outlier detection comes back
in Module 4's data-quality checks.

</details>

**Exercise 5 · Fill the gaps.** Replace `nan` in `values` with the mean of the other values, rounded
to 2 decimals.

<details class="solution"><summary>Solution</summary>

```python
filled = np.where(np.isnan(values), np.nanmean(values), values)
print(filled.round(2))
```

```text
[55000.   900.  1800.   400.  1200. 11860.]
```

</details>
