# Fields: Types, Defaults and Constraints

Use `Field()` to attach defaults, constraints and metadata.

```python
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, description="Price in EUR")
    quantity: int = Field(default=0, ge=0)
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$")
    discount: float = Field(default=0.0, ge=0, le=1)


p = Product(name="Keyboard", price=49.99, sku="KEY-0001")
print(p)
```

## Common `Field` arguments

| Argument | Applies to | Meaning |
|---|---|---|
| `default` / `default_factory` | any | static default / callable producing a default |
| `gt`, `ge`, `lt`, `le` | numbers | >, >=, <, <= |
| `multiple_of` | numbers | value must be a multiple |
| `min_length`, `max_length` | str, list, set, dict | size bounds |
| `pattern` | str | regex the string must match |
| `alias` | any | external name for the field |
| `description`, `examples`, `title` | any | documentation; flows into JSON Schema |
| `exclude` | any | omit from serialization |
| `frozen` | any | field cannot be reassigned |
| `repr` | any | hide from `repr()` (e.g. secrets) |

## Useful built-in types

```python
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, EmailStr, HttpUrl, SecretStr, PositiveInt


class Account(BaseModel):
    email: EmailStr           # needs pydantic[email]
    website: HttpUrl
    password: SecretStr       # hidden in repr and dumps
    balance: Decimal
    age: PositiveInt
    birthday: date


acc = Account(
    email="lenin@example.com",
    website="https://example.com",
    password="hunter2",
    balance="1024.50",
    age=31,
    birthday="1994-03-22",
)
print(acc.password)                     # **********
print(acc.password.get_secret_value())  # hunter2
```
