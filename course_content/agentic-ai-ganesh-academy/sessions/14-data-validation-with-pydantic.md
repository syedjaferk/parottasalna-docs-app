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

## Try it yourself

1. Add `email: EmailStr` to the `User` in `1.py_val.py` and try `"not-an-email"`.
2. Add a validator to `SignupRequest` that rejects passwords without a digit.
3. In `5.nested.py`, add a `model_validator` that checks `total_amount` equals the sum of
   `quantity × price`. The sample data passes (2 × 500 + 1 × 200 = 1,200); change a price and watch
   it fail.
4. Run `6.app.py` with `uvicorn` and open <http://localhost:8000/docs>. The docs page is generated
   from your models.
5. Extend `MovieReview` with `genres: list[str]` and `year: int`, and ask about three movies.

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
