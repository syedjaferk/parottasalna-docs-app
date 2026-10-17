# Session 6 · Checking responses with catch_response

## The big idea

By default Locust calls a request a success unless the server returns an error status (400 and above). But a reply can be
"200 OK" and still be wrong: the page is empty, the token is missing, the answer took far too long. `catch_response=True`
lets you inspect the reply and mark it **success** or **failure** yourself. It also lets you treat an expected error
(such as a 404 you want to test) as a success.

**Everyday example:** a parcel delivery. "Delivered" on the tracking page is not enough; you open the box and check that
the right item is inside and undamaged. A 200 status is the "delivered" message, and `catch_response` is opening the box.

```{raw} html
:file: ../diagrams/locust-validate.html
```

## Four checks

```{literalinclude} ../code/06_validate.py
:language: python
```

- **`login_has_token`** passes only if the JSON body contains a `token`.
- **`missing_product_is_expected`** asks for product 99. A 404 would normally count as a failure; here it is the
  correct answer, so we call `response.success()`.
- **`slow_page`** fails any response slower than 0.25 s. The shop's `/slow` takes 0.3 s on purpose, so this check
  fails every time.
- **`flaky_page`** has no check at all: the shop returns a 500 on every fourth call and Locust reports it by itself.

```bash
locust -f 06_validate.py --headless -u 4 -r 4 -t 8s --host http://127.0.0.1:8765 --only-summary --loglevel WARNING
```

```{literalinclude} ../code/06_validate.out
:language: text
```

## What the results mean

- **`/products/[missing]` has 0 failures** even though every reply was a 404, because we marked them as expected.
- **`/slow` shows 100% failures.** The status was 200, but our rule rejected it. The Error report lists the reason
  text passed to `failure()`, which is why a clear message such as `too slow: 0.30s` is worth writing.
- **`/flaky` failed about a quarter of the time** (the server fails every 4th call). Locust grouped them as
  `HTTPError('500 Server Error ...')`.
- **`/login` passed every time**, so the body check found the token.

Without these checks, the test would show 0% failures for `/slow` and for a login that returns an empty token, and you would
wrongly think the service is healthy.

## Common mistakes

- **Forgetting `with ... as response`.** With `catch_response=True` the request is only recorded when the `with` block ends.
- **Calling neither `success()` nor `failure()`.** If you do nothing the status code decides, which is not what you intended.
- **Parsing JSON without protection.** If the body is not JSON, `response.json()` raises an error. Wrap it, or check
  `response.text` first.
- **Using a vague reason.** "failed" tells nobody anything. Include the status or the missing field.
- **Setting the threshold below the real speed of your service**, as we did on purpose for `/slow`. Base thresholds on what
  your users need.

## Hands-on exercises

**Exercise 1.** Change the `slow_page` threshold to 0.5 s. What happens to the `/slow` failure count?

<details class="solution"><summary>Solution</summary>

It drops to 0, because the 0.3 s responses are now under the limit. The row still shows an average near 300 ms:
passing a check does not make the request faster.

</details>

**Exercise 2.** Make `/profile` (without a token) count as a success when the server answers 401.

<details class="solution"><summary>Solution</summary>

```python
@task
def profile_without_login(self):
    with self.client.get("/profile", name="/profile [no token]", catch_response=True) as response:
        if response.status_code == 401:
            response.success()
```

The shop returns 401 when no token is sent, so this request is recorded as a success.

</details>

**Exercise 3.** Fail a request if the product list is empty.

<details class="solution"><summary>Solution</summary>

```python
with self.client.get("/products", catch_response=True) as response:
    if len(response.json()) == 0:
        response.failure("empty product list")
```

A 200 response with `[]` would then be reported as a failure with that reason.

</details>

## Practice

Take the **Session 6 quiz**. The original page *Using catch_response for Custom Response Validation* is in the
reference section.
