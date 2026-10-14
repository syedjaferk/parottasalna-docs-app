# Session 6 · Adapter pattern

## The big idea

You have code that expects one interface, and a library that offers a different one. You can't (or
don't want to) change either. The **Adapter** pattern is a small class in the middle that translates
one interface into the other.

**Everyday example:** a travel plug adapter. Your Indian charger has round pins and the UK socket
has flat pins. You don't rewire the socket or the charger. You add an adapter.

:::{admonition} In plain words
:class: tip
Two pieces of code that should work together speak different "languages" (method names, units). Put a small **translator** in between instead of changing either side.

**Reach for it when:**

- a library's methods or data don't match what your code expects
- you can't (or shouldn't) change either side
- you want to switch providers without touching the rest of your app
:::

## Without Adapter

`0.no_adapter.py`: two payment providers with different method names.

```python
class RazorpayClient:
    def make_payment(self, rupees: float):
        print(f"Razorpay charged ₹{rupees}")

class StripeClient:
    def charge(self, amount_in_paise: int):
        print(f"Stripe charged {amount_in_paise} paise")

def checkout(provider, rupees):
    if isinstance(provider, RazorpayClient):
        provider.make_payment(rupees)
    elif isinstance(provider, StripeClient):
        provider.charge(int(rupees * 100))
```

`checkout` knows about every provider. A third provider means another `elif`.

## With Adapter

`1.adapter.py`: define the interface **you** want, then wrap each provider.

```python
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, rupees: float): ...

class RazorpayAdapter(PaymentGateway):
    def __init__(self, client: RazorpayClient):
        self._client = client
    def pay(self, rupees):
        self._client.make_payment(rupees)

class StripeAdapter(PaymentGateway):
    def __init__(self, client: StripeClient):
        self._client = client
    def pay(self, rupees):
        self._client.charge(int(rupees * 100))     # translate rupees → paise

def checkout(gateway: PaymentGateway, rupees: float):
    gateway.pay(rupees)

checkout(RazorpayAdapter(RazorpayClient()), 499)
checkout(StripeAdapter(StripeClient()), 499)
```

```text
Razorpay charged ₹499
Stripe charged 49900 paise
```

`checkout` only knows `PaymentGateway`. All the translation lives inside the adapters.

```{raw} html
:file: ../diagrams/s06-adapter.html
```

## Adapter + AI: one interface for many LLM SDKs

Every provider has its own call style (`2.llm_adapter.py`):

```python
class LLM(ABC):
    @abstractmethod
    def ask(self, prompt: str) -> str: ...

class OpenAIAdapter(LLM):
    def __init__(self, client):
        self.client = client
    def ask(self, prompt):
        r = self.client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return r.choices[0].message.content

class OllamaAdapter(LLM):
    def __init__(self, client):
        self.client = client
    def ask(self, prompt):
        r = self.client.generate(model="llama3", prompt=prompt)
        return r["response"]
```

The rest of your app calls `llm.ask("...")` and does not care which SDK sits underneath.

## Adapter vs Facade vs Decorator

- **Adapter** changes an interface into a different one.
- **Facade** (session 8) gives a simpler interface to a big system.
- **Decorator** (session 7) keeps the same interface and adds behaviour.

## Common mistakes

- **Putting business logic in the adapter.** It should only translate: names, units, formats.
- **Leaking the wrapped object's errors.** Convert provider exceptions into your own error type.
- **Writing an adapter for code you own.** Just change the code.

## Hands-on exercises

**Exercise 1 · Temperature.** A sensor library returns Fahrenheit but your app expects Celsius. Write
an adapter.

<details class="solution"><summary>Solution</summary>

```python
class FahrenheitSensor:
    def read_f(self): return 98.6

class CelsiusSensor(ABC):
    @abstractmethod
    def read_c(self) -> float: ...

class SensorAdapter(CelsiusSensor):
    def __init__(self, sensor: FahrenheitSensor):
        self._s = sensor
    def read_c(self):
        return round((self._s.read_f() - 32) * 5 / 9, 1)

print(SensorAdapter(FahrenheitSensor()).read_c())    # 37.0
```

</details>

**Exercise 2 · Convert errors.** Wrap `StripeClient.charge` so any exception becomes a
`PaymentError`.

<details class="solution"><summary>Solution</summary>

```python
class PaymentError(Exception):
    pass

class StripeAdapter(PaymentGateway):
    def __init__(self, client):
        self._client = client
    def pay(self, rupees):
        try:
            self._client.charge(int(rupees * 100))
        except Exception as e:
            raise PaymentError(f"Stripe failed: {e}") from e
```

</details>

**Exercise 3 · JSON to CSV.** Your report code expects an object with `rows()` returning lists. An
API gives a list of dicts. Adapt it.

<details class="solution"><summary>Solution</summary>

```python
class ApiData:
    def __init__(self, items): self.items = items   # list of dicts

class RowSource(ABC):
    @abstractmethod
    def rows(self) -> list[list]: ...

class ApiDataAdapter(RowSource):
    def __init__(self, data: ApiData):
        self._d = data
    def rows(self):
        return [list(item.values()) for item in self._d.items]

print(ApiDataAdapter(ApiData([{"a": 1, "b": 2}])).rows())    # [[1, 2]]
```

</details>

## Full source

<details class="source">
<summary>1.adapter.py</summary>

```{literalinclude} ../code/06-adapter/1.adapter.py
:language: python
```

</details>

<details class="source">
<summary>2.llm_adapter.py</summary>

```{literalinclude} ../code/06-adapter/2.llm_adapter.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_adapter.py <../code/06-adapter/0.no_adapter.py>` ·
{download}`1.adapter.py <../code/06-adapter/1.adapter.py>` ·
{download}`2.llm_adapter.py <../code/06-adapter/2.llm_adapter.py>`
