# Session 8 · Consuming REST APIs with requests

## The big idea

A lot of business data lives behind **APIs**: payments, CRM, ads, weather, government open data.
To ingest it, your code sends an HTTP request to a URL (an **endpoint**) and gets back **JSON**. The
skill isn't the first request; it's handling everything around it reliably: parameters, pages,
authentication, timeouts, errors, retries and rate limits.

**Everyday example:** ordering at a counter. You ask for something specific (the request), you get
it or a reason why not (the status code), the menu comes one page at a time (pagination), and if the
counter is busy you wait and try again (retries).

We use [JSONPlaceholder](https://jsonplaceholder.typicode.com), a free practice API with fixed fake
data, so you'll get the same results as this page. Run the examples in order.

```{raw} html
:file: ../diagrams/s08-api.html
```

## The first request

```python
import requests

BASE = "https://jsonplaceholder.typicode.com"

response = requests.get(f"{BASE}/users/1", timeout=10)
print(response.status_code, response.headers["Content-Type"])
user = response.json()                       # JSON body → Python dict
print(user["name"], "|", user["email"], "|", user["address"]["city"])
```

```text
200 application/json; charset=utf-8
Leanne Graham | Sincere@april.biz | Gwenborough
```

:::{warning}
**Always pass `timeout=`.** Without it, `requests` waits **forever** if the server never answers,
and your pipeline hangs silently. 10–30 seconds is typical.
:::

### Status codes you must handle

| Code | Meaning | What your pipeline should do |
|---|---|---|
| 200 / 201 | OK / created | use the data |
| 400 | bad request: your parameters are wrong | fix the code; don't retry |
| 401 / 403 | not signed in / not allowed | check the API key; don't retry |
| 404 | not found | skip or record it; don't retry |
| 429 | too many requests | wait (see `Retry-After`) and retry |
| 500 / 502 / 503 / 504 | the server's problem | retry with a growing wait |

`raise_for_status()` turns any 4xx/5xx into an exception, so errors can't slip through quietly:

```python
response = requests.get(f"{BASE}/users/999", timeout=10)
print(response.status_code, response.text)
try:
    response.raise_for_status()
except requests.HTTPError as e:
    print("HTTPError:", e)
```

```text
404 {}
HTTPError: 404 Client Error: Not Found for url: https://jsonplaceholder.typicode.com/users/999
```

## Query parameters

Let `requests` build the URL from a dict. It encodes spaces and special characters for you:

```python
response = requests.get(f"{BASE}/todos", params={"userId": 1, "completed": "true"}, timeout=10)
todos = response.json()
print(response.url)
print(len(todos), todos[0]["title"])
```

```text
https://jsonplaceholder.typicode.com/todos?userId=1&completed=true
11 et porro tempora
```

## Pagination: get every page

APIs return big collections in **pages**. Loop until a page comes back empty (other APIs use a
"next" link or a cursor, but the loop looks the same):

```python
def fetch_all(path, page_size=25):
    page, items = 1, []
    while True:
        r = requests.get(f"{BASE}/{path}", params={"_page": page, "_limit": page_size}, timeout=10)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        items.extend(batch)
        print(f"page {page}: {len(batch)} items (server says {r.headers.get('x-total-count')} in total)")
        page += 1
    return items

posts = fetch_all("posts")
print(len(posts), "posts")
```

```text
page 1: 25 items (server says 100 in total)
page 2: 25 items (server says 100 in total)
page 3: 25 items (server says 100 in total)
page 4: 25 items (server says 100 in total)
100 posts
```

## Sessions, headers and authentication

A `requests.Session` reuses the network connection (much faster for many calls) and keeps headers
you set once. Real APIs need a key, usually in a header. **Never write the key in your code**: read it
from an environment variable (Session 9):

```python
import os

session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "User-Agent": "parottasalna-de-course/1.0",
    "Authorization": f"Bearer {os.environ.get('SHOP_API_TOKEN', 'demo-token')}",
})
r = session.get(f"{BASE}/users/2", timeout=10)
print(r.status_code, r.json()["name"])
print(r.request.headers["User-Agent"])
```

```text
200 Ervin Howell
parottasalna-de-course/1.0
```

## Sending data: POST

```python
r = requests.post(f"{BASE}/posts", json={"title": "pipeline finished", "body": "12 rows", "userId": 1}, timeout=10)
print(r.status_code, r.json())
```

```text
201 {'title': 'pipeline finished', 'body': '12 rows', 'userId': 1, 'id': 101}
```

`json=` turns the dict into JSON and sets the right `Content-Type` header. (JSONPlaceholder pretends
to save it; the real data doesn't change.)

## Retries with backoff

Don't write retry loops by hand for HTTP: `requests` can retry automatically using `urllib3`'s
`Retry`, waiting longer each time and honouring `Retry-After` on 429s:

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry = Retry(
    total=5,                                    # at most 5 retries
    backoff_factor=1,                           # waits about 1, 2, 4, 8… seconds
    status_forcelist=[429, 500, 502, 503, 504], # retry only these
    allowed_methods=["GET"],                    # never automatically repeat a POST
    respect_retry_after_header=True,
)
api = requests.Session()
api.mount("https://", HTTPAdapter(max_retries=retry))

print(api.get(f"{BASE}/users/3", timeout=10).json()["name"])
```

```text
Clementine Bauch
```

Why only GET? Repeating a POST could create the same order twice. Only retry requests that are
safe to repeat (**idempotent**), an idea you'll meet again with pipeline backfills in Module 4.

## Land the raw data, then transform

A good ingestion step saves the API response **as it came** (the *raw* or *bronze* layer), then
transforms a copy. If your transformation has a bug, you can rerun it without calling the API
again:

```python
import json
from datetime import date
from pathlib import Path

raw_dir = Path("output/raw/users") / f"dt={date(2025, 1, 3)}"     # partitioned by day
raw_dir.mkdir(parents=True, exist_ok=True)

users = api.get(f"{BASE}/users", timeout=10).json()
with open(raw_dir / "users.jsonl", "w", encoding="utf-8") as f:
    for u in users:
        f.write(json.dumps(u) + "\n")

# transform: keep a flat, tidy subset
flat = [{"id": u["id"], "name": u["name"], "city": u["address"]["city"], "company": u["company"]["name"]}
        for u in users]
print(raw_dir.as_posix(), "→", len(users), "users saved raw")
print(flat[0])
```

```text
output/raw/users/dt=2025-01-03 → 10 users saved raw
{'id': 1, 'name': 'Leanne Graham', 'city': 'Gwenborough', 'company': 'Romaguera-Crona'}
```

The `dt=YYYY-MM-DD` folder naming is the convention Spark, Databricks and Hive use for **partitions**.

## Rate limits

Public APIs limit how often you can call them. Be polite even when they don't say so:

- add a short `time.sleep()` between calls in a loop;
- on a `429`, wait for `Retry-After` seconds (the `Retry` setup above does this);
- cache responses you've already fetched instead of calling again.

## Common mistakes

- **No timeout**: the pipeline hangs forever.
- **Not checking the status**: a 500 error page parsed as data, or `response.json()` crashing on HTML.
- **API keys in code or in Git.** Use environment variables or a secrets manager.
- **Retrying everything**, including 400/401/404 (they won't fix themselves) or POSTs (duplicates).
- **Fetching only page 1** and silently missing the rest.

## Hands-on exercises

**Exercise 1 · Who wrote the most?** Fetch all posts and count posts per `userId`. Which users have
the most?

<details class="solution"><summary>Solution</summary>

```python
from collections import Counter

posts = requests.get(f"{BASE}/posts", timeout=10).json()
counts = Counter(p["userId"] for p in posts)
print(counts.most_common(3))
```

```text
[(1, 10), (2, 10), (3, 10)]
```

It's practice data, so every user wrote exactly 10.

</details>

**Exercise 2 · Comments for one post.** Fetch `/posts/1/comments` and print the email domains of the
commenters, without duplicates and sorted.

<details class="solution"><summary>Solution</summary>

```python
comments = requests.get(f"{BASE}/posts/1/comments", timeout=10).json()
print(sorted({c["email"].split("@")[1] for c in comments}))
```

```text
['althea.biz', 'alysha.tv', 'gardner.biz', 'garfield.biz', 'sydney.com']
```

</details>

**Exercise 3 · Handle a missing record.** Write `get_user(user_id)` that returns the user dict, or
`None` for a 404, and raises for any other error.

<details class="solution"><summary>Solution</summary>

```python
def get_user(user_id):
    r = requests.get(f"{BASE}/users/{user_id}", timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()

print(get_user(5)["name"], get_user(500))
```

```text
Chelsey Dietrich None
```

</details>

**Exercise 4 · Join two endpoints.** Fetch `/users` and `/todos`, then print each user's name with the
number of **unfinished** todos, for the first 3 users.

<details class="solution"><summary>Solution</summary>

```python
users = {u["id"]: u["name"] for u in requests.get(f"{BASE}/users", timeout=10).json()}
todos = requests.get(f"{BASE}/todos", timeout=10).json()
open_count = Counter(t["userId"] for t in todos if not t["completed"])
for uid in list(users)[:3]:
    print(users[uid], open_count[uid])
```

```text
Leanne Graham 9
Ervin Howell 12
Clementine Bauch 13
```

The same "build a lookup dict, then join" pattern from Session 5.

</details>

**Exercise 5 · Save as Parquet.** Turn the flattened `users` into a pandas DataFrame and save it to
`output/users.parquet`. Print the columns.

<details class="solution"><summary>Solution</summary>

```python
import pandas as pd

df = pd.DataFrame(flat)
df.to_parquet("output/users.parquet", index=False)
print(pd.read_parquet("output/users.parquet").columns.tolist())
```

```text
['id', 'name', 'city', 'company']
```

</details>
