# Session 14 · Data validation with Pydantic

## The big idea

Data from outside your program (a web form, an API, **an LLM's answer**) can be missing, the wrong
type or nonsense. **Pydantic** lets you describe the shape you expect as a Python class. It checks
the data, converts what it safely can (`"9"` → `9`), and raises a clear error for the rest.

**Everyday example:** a form at the bank. The clerk checks that every box is filled in, the date is
a real date and the amount is a number, before anything gets processed.

## Without Pydantic

`0.basic_val.py` checks by hand:

```python
def create_user(data: dict):
    if "name" not in data or not isinstance(data["name"], str):
        raise ValueError("name is required and must be a string")
    if "age" not in data or not isinstance(data["age"], int):
        raise ValueError("age is required and must be an int")
    if data["age"] < 0:
        raise ValueError("age must be positive")

create_user({"name": "Syed Jafer K", "age": "29", "year": 1997})
```

```text
ValueError: age is required and must be an int
```

Three `if`s for two fields. A real model with 15 fields is hundreds of lines.

## With Pydantic

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(gt=0)

User(name="Kavya", age="9")        # name='Kavya' age=9   ← "9" safely converted to 9
User(name="Kavya", age=-3)
```

```text
1 validation error for User
age
  Input should be greater than 0 [type=greater_than, input_value=-3, input_type=int]
```

```text
User(name="Kavya", age="nine")
1 validation error for User
age
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='nine', input_type=str]
```

```{raw} html
:file: ../diagrams/s14-validate.html
```

The error says **which field**, **what's wrong** and **what was sent**.

## Models in practice

**Converting back** (`2.py`):

```python
p = Product(id=1, name="Keyboard", price=999.0, in_stock=True)
p.model_dump()        # {'id': 1, 'name': 'Keyboard', 'price': 999.0, 'in_stock': True}
p.model_dump_json()   # '{"id":1,"name":"Keyboard","price":999.0,"in_stock":true}'
```

**Defaults, optional fields and rules** (`3.fields.py`):

```python
class User(BaseModel):
    username: str
    is_active: bool = True                       # default
    bio: str | None = None                       # optional
    tags: list[str] = Field(default_factory=list)   # never write `= []`

class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    age: int = Field(ge=13, le=120, description="User age in years")
    email: EmailStr                              # needs: pip install "pydantic[email]"
    password: str = Field(min_length=8)
```

**Your own rules** (`4.adv_field_val.py`):

```python
@field_validator("username")
@classmethod
def no_spaces(cls, v: str) -> str:
    if " " in v:
        raise ValueError("username must not contain spaces")
    return v
```

**Nested models** (`5.nested.py`): an `Order` holds a `Customer`, who holds an `Address`, plus a
list of `OrderItem`s. One call validates the whole tree:

```python
order = Order(**order_data)
print(order.customer.address.city)    # Coimbatore
```

## FastAPI uses Pydantic for you

`6.app.py`: the request body is checked against `UserCreate` **before** your function runs. The
response is filtered through `UserOut`, so the password can never leak back out:

```python
@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate):
    return {"id": 1, "username": user.username, "email": user.email}
```

Send a bad email and FastAPI replies **422** with the Pydantic error. You wrote no validation code.

## Pydantic + LLMs: structured output

Asking for *"Name | Rating | Summary"* and splitting the text is fragile (`7.lc_normal.py`):

```python
rating = int(parts[1].strip())   # crashes if the model writes "9/10" or "Rating: 9"
```

Instead, give LangChain a Pydantic model (`8.lc_with_pydantic.py`):

```python
class MovieReview(BaseModel):
    name: str = Field(description="Movie title")
    rating: int = Field(ge=1, le=10, description="Rating out of 10")
    summary: str = Field(description="One-line summary")

structured_llm = llm.with_structured_output(MovieReview)
result = structured_llm.invoke("Give me details for the movie Interstellar")
```

```text
name='Interstellar' rating=9 summary='A team of explorers travels through a wormhole …'
<class '__main__.MovieReview'>
```

You get a real object with an `int` between 1 and 10, or an error, never a half-parsed string. The
`description`s are sent to the model, so write them for the model to read.

## Common mistakes

- **`= []` as a default.** Use `Field(default_factory=list)`.
- **Validating LLM output with `json.loads` and hope.** Use `with_structured_output` or
  `Model.model_validate_json(text)`.
- **Catching the error and carrying on.** If the data is invalid, stop or ask again; don't continue
  with half-checked values.
- **Expecting strict types.** Pydantic converts `"9"` to `9` by default. If you need exactly an
  `int`, use `Field(strict=True)`.

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · Email validation.** Add `email: EmailStr` to the `User` in `1.py_val.py` and try
`"not-an-email"`.

<details class="solution"><summary>Solution</summary>

```python
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    name: str
    age: int = Field(gt=0)
    email: EmailStr

User(name="Kavya", age=9, email="not-an-email")
# value is not a valid email address: An email address must have an @-sign.
```

`EmailStr` needs `pip install "pydantic[email]"`.

</details>

**Exercise 2 · Password rule.** Reject passwords without a digit.

<details class="solution"><summary>Solution</summary>

```python
@field_validator("password")
@classmethod
def needs_a_digit(cls, v: str) -> str:
    if not any(ch.isdigit() for ch in v):
        raise ValueError("password must contain at least one digit")
    return v
```

</details>

**Exercise 3 · Check the total.** In `5.nested.py`, check that `total_amount` equals the sum of
`quantity × price`.

<details class="solution"><summary>Solution</summary>

```python
from pydantic import model_validator

class Order(BaseModel):
    ...
    @model_validator(mode="after")
    def total_matches_items(self):
        expected = sum(item.quantity * item.price for item in self.items)
        if abs(expected - self.total_amount) > 0.01:
            raise ValueError(f"total_amount {self.total_amount} != items total {expected}")
        return self
```

The sample passes (2 × 500 + 1 × 200 = 1,200). Change the mouse price to 600 and it fails.

</details>

**Exercise 4 · Free API docs.** Run `6.app.py` and open the docs page.

<details class="solution"><summary>How</summary>

```bash
uvicorn 6.app:app --reload        # fails: module names can't start with a digit
cp 6.app.py users_api.py && uvicorn users_api:app --reload
```

Open <http://localhost:8000/docs>. Try **POST /users** with a bad email: FastAPI answers **422** with
the Pydantic error, and the response never contains the password.

</details>

**Exercise 5 · Richer structured output.** Add `genres: list[str]` and `year: int` to `MovieReview`
and ask about three movies.

<details class="solution"><summary>Solution</summary>

```python
class MovieReview(BaseModel):
    name: str = Field(description="Movie title")
    year: int = Field(ge=1888, le=2100, description="Release year")
    genres: list[str] = Field(description="1-3 genres, lowercase")
    rating: int = Field(ge=1, le=10, description="Rating out of 10")
    summary: str = Field(description="One-line summary")

for title in ["Interstellar", "Baahubali", "Jailer"]:
    print(structured_llm.invoke(f"Give me details for the movie {title}"))
```

Remember to rebuild `structured_llm = llm.with_structured_output(MovieReview)` after changing the
model.

</details>

**Exercise 6 · Validate LLM JSON yourself.** Without `with_structured_output`, ask for JSON and
validate it with `model_validate_json`.

<details class="solution"><summary>Solution</summary>

```python
from pydantic import ValidationError

text = llm.invoke("Return ONLY JSON with keys name, rating (1-10), summary for Interstellar").content
try:
    review = MovieReview.model_validate_json(text)
except ValidationError as e:
    print("Bad output from the model:", e)
```

If the model wraps the JSON in ```` ```json ```` fences, strip them first, which is one more reason
to prefer `with_structured_output`.

</details>

## Full source

<details class="source">
<summary>3.fields.py</summary>

```{literalinclude} ../code/14-pydantic/3.fields.py
:language: python
```

</details>

<details class="source">
<summary>5.nested.py</summary>

```{literalinclude} ../code/14-pydantic/5.nested.py
:language: python
```

</details>

<details class="source">
<summary>6.app.py</summary>

```{literalinclude} ../code/14-pydantic/6.app.py
:language: python
```

</details>

<details class="source">
<summary>8.lc_with_pydantic.py</summary>

```{literalinclude} ../code/14-pydantic/8.lc_with_pydantic.py
:language: python
```

</details>

**Downloads:**
{download}`0.basic_val.py <../code/14-pydantic/0.basic_val.py>` ·
{download}`1.py_val.py <../code/14-pydantic/1.py_val.py>` ·
{download}`2.py <../code/14-pydantic/2.py>` ·
{download}`3.fields.py <../code/14-pydantic/3.fields.py>` ·
{download}`4.adv_field_val.py <../code/14-pydantic/4.adv_field_val.py>` ·
{download}`5.nested.py <../code/14-pydantic/5.nested.py>` ·
{download}`6.app.py <../code/14-pydantic/6.app.py>` ·
{download}`7.lc_normal.py <../code/14-pydantic/7.lc_normal.py>` ·
{download}`8.lc_with_pydantic.py <../code/14-pydantic/8.lc_with_pydantic.py>`
