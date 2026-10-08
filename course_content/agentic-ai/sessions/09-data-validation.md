# Session 9 · Data Validation with Pydantic

## The big idea

Data that comes into your program, from a form, a website or an **AI model**, can be wrong: a
missing field, text where a number should be, an age of -9. **Validation** means checking data
**before** you use it. **Pydantic** lets you describe the shape you expect once, as a class, and
then checks everything for you.

**Everyday example:** the security gate at an airport. You define the rules once (boarding pass,
ID, no liquids over 100 ml). Every passenger is checked against them. Problems are caught at the
gate, not on the plane.

```{raw} html
:file: ../diagrams/s09-gate.html
```

## The hard way: checking by hand

```python
def create_user(data: dict):
    if "name" not in data or not isinstance(data["name"], str):
        raise ValueError("name is required and must be a string")
    if "age" not in data or not isinstance(data["age"], int):
        raise ValueError("age is required and must be an int")
    if data["age"] < 0:
        raise ValueError("age must be positive")
```

Six lines for two fields. Imagine twenty fields with addresses and lists. It also stops at the
**first** problem, so you fix one mistake, run again, find the next…

## The easy way: Pydantic

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(gt=0)      # gt = "greater than"

user = User(name="Kavya", age=-9)
```

**Output:**

```text
ValidationError: 1 validation error for User
age
  Input should be greater than 0 [type=greater_than, input_value=-9]
```

The error tells you **which field**, **which rule** and **what value** broke it, and it lists
**every** problem at once.

## Using a model

```python
class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool

p = Product(id=1, name="Keyboard", price=999.0, in_stock=True)

p.name               # 'Keyboard'
p.model_dump()       # {'id': 1, 'name': 'Keyboard', 'price': 999.0, 'in_stock': True}   ← dict
p.model_dump_json()  # '{"id":1,"name":"Keyboard","price":999.0,"in_stock":true}'       ← JSON text
```

Pydantic is also helpful with "almost right" data:

| You pass | You get |
|---|---|
| `id="1"` (text that looks like a number) | `id=1` ✅ converted for you |
| `id="abc"` | ❌ `ValidationError`: not a valid integer |

## Defaults, optional fields and rules

```python
from pydantic import BaseModel, EmailStr, Field

class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    age: int = Field(ge=13, le=120)       # between 13 and 120
    email: EmailStr                       # must look like an email
    password: str = Field(min_length=8)
    bio: str | None = None                # optional: may be missing
    is_active: bool = True                # default value if missing
    tags: list[str] = Field(default_factory=list)   # a fresh empty list for each user
```

| Rule | Meaning |
|---|---|
| `gt` / `ge` | greater than / greater than or equal |
| `lt` / `le` | less than / less than or equal |
| `min_length` / `max_length` | how long text (or a list) may be |
| `str \| None = None` | optional field |
| `description="..."` | an explanation. AI models read this too! |

:::{note}
`EmailStr` needs one extra package: `pip install "pydantic[email]"`.
:::

:::{tip}
**Why `default_factory=list`?** Inside a Pydantic model, `tags: list[str] = []` happens to be safe.
But the same habit in a normal function, `def add(item, items=[])`, is a classic bug: **one** list
gets shared by every call. `default_factory=list` says "make a fresh empty list each time" and is
correct everywhere.
:::

## Your own rules: `@field_validator`

When the built-in rules aren't enough, write your own check:

```python
from pydantic import BaseModel, field_validator

class SignupRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("username must not contain spaces")
        return v           # always give the value back
```

```python
SignupRequest(username="syed jafer", password="secret123")
# ValidationError: username — Value error, username must not contain spaces
```

## Models inside models

Real data has layers: an order has a customer, the customer has an address, the order has items.

```{raw} html
:file: ../diagrams/s09-nested.html
```

```python
class Address(BaseModel):
    street: str
    city: str
    pincode: str

class Customer(BaseModel):
    name: str
    email: str
    address: Address              # a model inside a model

class OrderItem(BaseModel):
    product_name: str
    quantity: int
    price: float

class Order(BaseModel):
    order_id: int
    customer: Customer
    items: list[OrderItem]        # a list of models
    total_amount: float

order = Order(**order_data)       # checks the WHOLE structure in one go
order.customer.address.city       # 'Coimbatore'
```

`**order_data` "unpacks" a dictionary into named arguments. `Order.model_validate(order_data)` does
the same thing.

## FastAPI checks requests for you

FastAPI uses Pydantic models to check everything that comes in **and** goes out:

```python
class UserCreate(BaseModel):     # what the client must send
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):        # what we send back (note: no password!)
    id: int
    username: str
    email: EmailStr

@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate):
    new_user = {"id": 1, "username": user.username, "email": user.email}
    return new_user
```

- Send a bad email → you automatically get a **422** error listing the problems. Your function never runs.
- `response_model=UserOut` **filters** the response. Even if you accidentally return the password, it's removed.
- Free interactive docs appear at `/docs`.

## Clean answers from an AI model

This is where it all comes together. Asking for "Name | Rating | Summary" gives you text you have
to cut up, and hope:

```python
text = llm.invoke("Give me the name, rating out of 10 and a one-line summary for "
                  "Interstellar. Format: Name | Rating | Summary").content
rating = int(text.split("|")[1])    # 💥 crashes if the model writes "9/10" or "Rating: 9"
```

With Pydantic, you describe what you want and get a **real Python object** back:

```python
class MovieReview(BaseModel):
    name: str = Field(description="Movie title")
    rating: int = Field(ge=1, le=10, description="Rating out of 10")
    summary: str = Field(description="One-line summary")

structured_llm = llm.with_structured_output(MovieReview)
result = structured_llm.invoke("Give me details for the movie Interstellar")

print(result.rating)   # 9 ← always a whole number from 1 to 10
print(result.name)     # Interstellar
```

```{raw} html
:file: ../diagrams/s09-structured.html
```

`with_structured_output()` sends your model's shape (including the `description`s) to the AI,
then checks the reply. If the AI breaks a rule, you get a clear error instead of a silent wrong value.

## Try it yourself

1. Add a `@field_validator` that requires the password to contain at least one digit.
   (Hint: `any(ch.isdigit() for ch in v)`.)
2. Make an `Order` check that `total_amount` equals the sum of `quantity × price`. Search for
   Pydantic's `@model_validator(mode="after")`.
3. Make a `Recipe` model (`title`, `minutes: int`, `ingredients: list[str]`, `steps: list[str]`) and
   get one from the AI with `with_structured_output`.
4. Run `6.app.py` with `uvicorn`, open `/docs`, and send a wrong email. Read the 422 error.

## Full source

<details class="source"><summary>0.basic_val.py: validation by hand</summary>

```{literalinclude} ../code/09-data-validation/0.basic_val.py
:language: python
```

</details>

<details class="source"><summary>1.py_val.py: first Pydantic model</summary>

```{literalinclude} ../code/09-data-validation/1.py_val.py
:language: python
```

</details>

<details class="source"><summary>2.py: models and conversion</summary>

```{literalinclude} ../code/09-data-validation/2.py
:language: python
```

</details>

<details class="source"><summary>3.fields.py</summary>

```{literalinclude} ../code/09-data-validation/3.fields.py
:language: python
```

</details>

<details class="source"><summary>4.adv_field_val.py</summary>

```{literalinclude} ../code/09-data-validation/4.adv_field_val.py
:language: python
```

</details>

<details class="source"><summary>5.nested.py</summary>

```{literalinclude} ../code/09-data-validation/5.nested.py
:language: python
```

</details>

<details class="source"><summary>6.app.py: FastAPI</summary>

```{literalinclude} ../code/09-data-validation/6.app.py
:language: python
```

</details>

<details class="source"><summary>7.lc_normal.py: parsing strings by hand</summary>

```{literalinclude} ../code/09-data-validation/7.lc_normal.py
:language: python
```

</details>

<details class="source"><summary>8.lc_with_pydantic.py: structured output</summary>

```{literalinclude} ../code/09-data-validation/8.lc_with_pydantic.py
:language: python
```

</details>
