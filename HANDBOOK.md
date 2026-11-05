# The Pydantic Handbook

A practical guide to **Pydantic v2** — data validation, settings, and serialization in modern Python, with a focus on APIs and AI/LLM applications.

> Tested against **Pydantic 2.13** and **pydantic-settings 2.16** on Python 3.10+. Every code block in this handbook is runnable as-is.

---

## Table of Contents

1. [What Pydantic Is (and Isn't)](#1-what-pydantic-is-and-isnt)
2. [Installation](#2-installation)
3. [Your First Model](#3-your-first-model)
4. [Fields: Types, Defaults and Constraints](#4-fields-types-defaults-and-constraints)
5. [Validation Errors](#5-validation-errors)
6. [Strict vs Lax Mode](#6-strict-vs-lax-mode)
7. [Nested Models and Collections](#7-nested-models-and-collections)
8. [Custom Validators](#8-custom-validators)
9. [Computed Fields](#9-computed-fields)
10. [Serialization: `model_dump` and `model_dump_json`](#10-serialization-model_dump-and-model_dump_json)
11. [Aliases](#11-aliases)
12. [Model Configuration (`ConfigDict`)](#12-model-configuration-configdict)
13. [Annotated Types and Reusable Constraints](#13-annotated-types-and-reusable-constraints)
14. [Unions and Discriminated Unions](#14-unions-and-discriminated-unions)
15. [Generic Models](#15-generic-models)
16. [`TypeAdapter`: Validating Without a Model](#16-typeadapter-validating-without-a-model)
17. [`@validate_call`: Validating Function Arguments](#17-validate_call-validating-function-arguments)
18. [Dataclasses and `TypedDict`](#18-dataclasses-and-typeddict)
19. [Settings Management with `pydantic-settings`](#19-settings-management-with-pydantic-settings)
20. [JSON Schema Generation](#20-json-schema-generation)
21. [Pydantic with FastAPI](#21-pydantic-with-fastapi)
22. [Pydantic for LLM and AI Engineering](#22-pydantic-for-llm-and-ai-engineering)
23. [Performance Tips](#23-performance-tips)
24. [Migrating from v1 to v2](#24-migrating-from-v1-to-v2)
25. [Common Pitfalls](#25-common-pitfalls)
26. [Cheat Sheet](#26-cheat-sheet)

---

## 1. What Pydantic Is (and Isn't)

Pydantic is a **data validation and parsing library** driven by Python type hints. You describe the shape of your data with ordinary annotations, and Pydantic:

- **Validates** incoming data against those types and constraints.
- **Coerces** compatible input into the declared type (e.g. `"42"` → `42`) unless you ask for strict mode.
- **Serializes** objects back into dicts and JSON.
- **Generates JSON Schema** describing the model.

The core validation engine (`pydantic-core`) is written in Rust, which makes v2 dramatically faster than v1.

What Pydantic is **not**:

- Not an ORM — it doesn't talk to databases (though it pairs well with SQLAlchemy and SQLModel).
- Not a static type checker — it validates at **runtime**. Use mypy/pyright alongside it.
- Not a guarantee once the object exists — by default, assigning an invalid value to an attribute after creation is *not* re-validated (see `validate_assignment`).

**Rule of thumb:** use Pydantic at the **boundaries** of your system — HTTP requests, config files, environment variables, message queues, LLM outputs — anywhere untrusted data enters.

---

## 2. Installation

```bash
pip install pydantic                 # core library
pip install "pydantic[email]"        # adds EmailStr support
pip install pydantic-settings        # settings / env var management
```

Check the version:

```python
import pydantic
print(pydantic.VERSION)
```

---

## 3. Your First Model

```python
from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    signup_ts: datetime | None = None
    tags: list[str] = []


user = User(id="123", name="Lenin", signup_ts="2026-01-15T10:30:00")

print(user.id)          # 123  (str "123" coerced to int)
print(user.signup_ts)   # 2026-01-15 10:30:00  (str parsed into datetime)
print(user.tags)        # []
print(user.model_dump())
# {'id': 123, 'name': 'Lenin', 'signup_ts': datetime.datetime(2026, 1, 15, 10, 30), 'tags': []}
```

Key points:

- Fields without a default are **required**.
- `X | None = None` makes a field optional.
- Mutable defaults like `[]` are safe — Pydantic copies them per instance (unlike plain Python classes).

### Three ways to build a model

```python
User(id=1, name="A")                                 # keyword args
User.model_validate({"id": 1, "name": "A"})          # from a dict
User.model_validate_json('{"id": 1, "name": "A"}')   # from a JSON string (fastest path)
```

Prefer `model_validate_json` when you already have raw JSON — it parses and validates in one Rust pass instead of `json.loads` + validate.

---

## 4. Fields: Types, Defaults and Constraints

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

### Common `Field` arguments

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

### Useful built-in types

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

---

## 5. Validation Errors

When validation fails Pydantic raises a single `ValidationError` that collects **every** problem, not just the first.

```python
from pydantic import BaseModel, Field, ValidationError


class Order(BaseModel):
    order_id: int
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)


try:
    Order(order_id="abc", amount=-5, currency="EURO")
except ValidationError as e:
    print(e.error_count())  # 3
    for err in e.errors():
        print(err["loc"], err["type"], "-", err["msg"])
```

Output:

```
('order_id',) int_parsing - Input should be a valid integer, unable to parse string as an integer
('amount',) greater_than - Input should be greater than 0
('currency',) string_too_long - String should have at most 3 characters
```

Each error dict contains:

- `loc` — path to the failing field (tuples like `('items', 2, 'price')` for nested data)
- `type` — a stable machine-readable error code (good for i18n or API error mapping)
- `msg` — human-readable message
- `input` — the value that failed

`e.json()` gives the same as a JSON string — handy for API responses.

---

## 6. Strict vs Lax Mode

By default Pydantic runs in **lax mode**: it coerces sensible inputs (`"42"` → `42`, `"true"` → `True`). **Strict mode** refuses any type conversion.

```python
from pydantic import BaseModel, ConfigDict, Field, StrictInt, ValidationError


class Lax(BaseModel):
    count: int


class Strict(BaseModel):
    model_config = ConfigDict(strict=True)
    count: int


class Mixed(BaseModel):
    count: StrictInt               # strict on this field only
    ratio: float = Field(strict=False)


print(Lax(count="42").count)       # 42

try:
    Strict(count="42")
except ValidationError as e:
    print(e.errors()[0]["type"])   # int_type
```

You can also opt in per call: `Lax.model_validate(data, strict=True)`.

**When to use strict mode:** internal service-to-service contracts and financial data where silent coercion could hide bugs. Keep lax mode for user-facing inputs like query strings and form data, which always arrive as strings.

> Note: when validating JSON with `model_validate_json`, strict mode still allows types that JSON can't express natively — e.g. ISO strings for `datetime` or `UUID`.

---

## 7. Nested Models and Collections

Models compose naturally. Validation recurses through nested models, lists, dicts and tuples.

```python
from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    country: str = "NL"


class LineItem(BaseModel):
    sku: str
    qty: int
    unit_price: float


class Customer(BaseModel):
    name: str
    address: Address
    items: list[LineItem]
    metadata: dict[str, str] = {}
    coordinates: tuple[float, float] | None = None


c = Customer.model_validate({
    "name": "Lenin",
    "address": {"street": "Damrak 1", "city": "Amsterdam"},
    "items": [
        {"sku": "A1", "qty": "2", "unit_price": "9.99"},
        {"sku": "B2", "qty": 1, "unit_price": 20},
    ],
    "coordinates": [52.37, 4.89],
})

print(c.address.city)        # Amsterdam
print(c.items[0].qty)        # 2
print(c.coordinates)         # (52.37, 4.89)
```

Errors in nested data point to the exact location, e.g. `('items', 1, 'qty')`.

### Self-referencing models

```python
from __future__ import annotations
from pydantic import BaseModel


class TreeNode(BaseModel):
    value: int
    children: list[TreeNode] = []


tree = TreeNode(value=1, children=[{"value": 2}, {"value": 3, "children": [{"value": 4}]}])
print(tree.children[1].children[0].value)  # 4
```

---

## 8. Custom Validators

### Field validators

`@field_validator` runs on one or more specific fields. It must be a `@classmethod`.

```python
from pydantic import BaseModel, field_validator


class Signup(BaseModel):
    username: str
    email: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("must be alphanumeric")
        return v.lower()            # validators can also transform

    @field_validator("username", "email")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()
```

Raise `ValueError` or `AssertionError`; Pydantic wraps them into a `ValidationError`.

### Validator modes

| Mode | Runs | Receives | Use for |
|---|---|---|---|
| `"after"` (default) | after Pydantic's own validation | the typed value | business rules |
| `"before"` | before type validation | raw input (`Any`) | normalising messy input |
| `"wrap"` | around Pydantic's validation | value + `handler` | fallbacks, logging, retry logic |
| `"plain"` | instead of Pydantic's validation | raw input | full custom parsing |

```python
from typing import Any
from pydantic import BaseModel, ValidationError, ValidatorFunctionWrapHandler, field_validator


class Tags(BaseModel):
    tags: list[str]
    score: int

    @field_validator("tags", mode="before")
    @classmethod
    def split_csv(cls, v: Any) -> Any:
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        return v

    @field_validator("score", mode="wrap")
    @classmethod
    def default_on_failure(cls, v: Any, handler: ValidatorFunctionWrapHandler) -> int:
        try:
            return handler(v)
        except ValidationError:
            return 0


print(Tags(tags="ai, python , pydantic", score="oops"))
# tags=['ai', 'python', 'pydantic'] score=0
```

### Model validators (cross-field checks)

```python
from datetime import date
from typing import Self
from pydantic import BaseModel, model_validator


class Booking(BaseModel):
    check_in: date
    check_out: date
    password: str
    password_confirm: str

    @model_validator(mode="after")
    def check_dates_and_passwords(self) -> Self:
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        if self.password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self
```

> `typing.Self` needs Python 3.11+. On 3.10 use `from typing_extensions import Self`.

A `mode="before"` model validator receives the raw input (usually a dict) — useful for renaming legacy keys or unwrapping envelopes:

```python
from typing import Any
from pydantic import BaseModel, model_validator


class ApiResponse(BaseModel):
    id: int
    name: str

    @model_validator(mode="before")
    @classmethod
    def unwrap(cls, data: Any) -> Any:
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data


print(ApiResponse.model_validate({"data": {"id": 1, "name": "x"}}))
```

### Validation context

Pass runtime information (current user, allowed values from a DB) into validators:

```python
from pydantic import BaseModel, ValidationInfo, field_validator


class Doc(BaseModel):
    category: str

    @field_validator("category")
    @classmethod
    def check_allowed(cls, v: str, info: ValidationInfo) -> str:
        allowed = (info.context or {}).get("allowed_categories")
        if allowed is not None and v not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v


Doc.model_validate({"category": "ai"}, context={"allowed_categories": {"ai", "ml"}})
```

---

## 9. Computed Fields

`@computed_field` exposes a property in serialization and JSON Schema.

```python
from pydantic import BaseModel, computed_field


class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height


r = Rectangle(width=3, height=4)
print(r.model_dump())   # {'width': 3.0, 'height': 4.0, 'area': 12.0}
```

Computed fields are **output-only** — they're ignored if passed as input.

---

## 10. Serialization: `model_dump` and `model_dump_json`

```python
from datetime import datetime
from pydantic import BaseModel, Field


class Event(BaseModel):
    id: int
    title: str
    notes: str | None = None
    internal_score: float = Field(default=0.0, exclude=True)
    created: datetime


e = Event(id=1, title="Launch", created="2026-11-05T12:00:00")

e.model_dump()                       # Python objects (datetime stays datetime)
e.model_dump(mode="json")            # JSON-safe types (datetime -> str)
e.model_dump_json(indent=2)          # JSON string
e.model_dump(include={"id", "title"})
e.model_dump(exclude={"notes"})
e.model_dump(exclude_none=True)      # drop None values
e.model_dump(exclude_unset=True)     # only fields explicitly provided
e.model_dump(exclude_defaults=True)  # drop fields equal to their default
e.model_dump(by_alias=True)          # use aliases as keys
```

`exclude_unset=True` is the idiomatic way to implement **PATCH** endpoints:

```python
from pydantic import BaseModel


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


patch = UserUpdate(email="new@example.com")
print(patch.model_dump(exclude_unset=True))   # {'email': 'new@example.com'}
```

### Copying with changes

```python
updated = e.model_copy(update={"title": "Relaunch"})
```

`model_copy(update=...)` does **not** validate the update — validate first if the data is untrusted.

### Custom serializers

```python
from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, field_serializer, model_serializer


class Invoice(BaseModel):
    amount: Decimal
    issued: datetime

    @field_serializer("amount")
    def amount_as_str(self, v: Decimal) -> str:
        return f"{v:.2f}"

    @field_serializer("issued")
    def issued_as_date(self, v: datetime) -> str:
        return v.date().isoformat()


print(Invoice(amount="10.5", issued="2026-11-05T09:00:00").model_dump_json())
# {"amount":"10.50","issued":"2026-11-05"}


class Envelope(BaseModel):
    payload: dict[str, Any]

    @model_serializer(mode="wrap")
    def add_version(self, handler) -> dict[str, Any]:
        data = handler(self)
        data["api_version"] = "v1"
        return data
```

---

## 11. Aliases

Aliases bridge naming conventions — e.g. camelCase JSON to snake_case Python.

```python
from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class GitHubUser(BaseModel):
    login: str
    avatar: str = Field(alias="avatar_url")                                  # one external name
    full_name: str = Field(validation_alias=AliasChoices("name", "fullName"))  # accept several
    city: str = Field(validation_alias=AliasPath("location", "city"))       # pull from nested path


u = GitHubUser.model_validate({
    "login": "leninjoseph",
    "avatar_url": "https://x/y.png",
    "fullName": "Lenin Joseph",
    "location": {"city": "Chennai"},
})
print(u.full_name, u.city)


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    first_name: str
    last_name: str


m = CamelModel.model_validate({"firstName": "Lenin", "lastName": "Joseph"})
print(m.model_dump(by_alias=True))   # {'firstName': 'Lenin', 'lastName': 'Joseph'}
CamelModel(first_name="A", last_name="B")   # works because populate_by_name=True
```

- `alias` — used for both validation and serialization.
- `validation_alias` — input only.
- `serialization_alias` — output only (needs `by_alias=True`).

---

## 12. Model Configuration (`ConfigDict`)

```python
from pydantic import BaseModel, ConfigDict


class StrictApiModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",              # "ignore" (default) | "allow" | "forbid"
        frozen=True,                 # immutable + hashable
        str_strip_whitespace=True,
        str_min_length=1,
        validate_assignment=True,    # re-validate on attribute assignment
        validate_default=True,       # validate default values too
        use_enum_values=True,        # store enum .value instead of the member
        from_attributes=True,        # allow model_validate(orm_obj)
        populate_by_name=True,
    )
```

The settings you'll use most:

| Option | Why |
|---|---|
| `extra="forbid"` | Catch typos in client payloads (`"emial"` raises instead of being silently dropped). |
| `frozen=True` | Value objects, cache keys, safe sharing across threads. |
| `validate_assignment=True` | Keep the object valid after mutation. |
| `from_attributes=True` | Build models from ORM objects (SQLAlchemy) or any object with attributes. |

```python
from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class FakeOrmRow:
    def __init__(self):
        self.id = 7
        self.name = "Lenin"
        self.password_hash = "secret"   # not in the model -> not exposed


print(UserOut.model_validate(FakeOrmRow()))   # id=7 name='Lenin'
```

Config is **inherited** — define a project `BaseSchema` once and subclass it everywhere.

---

## 13. Annotated Types and Reusable Constraints

`typing.Annotated` lets you package a type plus its constraints and validators into a reusable alias.

```python
from typing import Annotated
from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, StringConstraints

Username = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, min_length=3, max_length=30)]
Percentage = Annotated[float, Field(ge=0, le=100)]


def must_be_even(v: int) -> int:
    if v % 2:
        raise ValueError("must be even")
    return v


EvenInt = Annotated[int, AfterValidator(must_be_even)]
CommaList = Annotated[list[str], BeforeValidator(lambda v: v.split(",") if isinstance(v, str) else v)]


class Profile(BaseModel):
    username: Username
    completion: Percentage
    lucky_number: EvenInt
    skills: CommaList


print(Profile(username="  LENIN ", completion=87.5, lucky_number=4, skills="python,ai,fastapi"))
# username='lenin' completion=87.5 lucky_number=4 skills=['python', 'ai', 'fastapi']
```

This is the cleanest way to share validation logic across many models — far better than copy-pasting `@field_validator`s.

---

## 14. Unions and Discriminated Unions

### Plain unions

```python
from pydantic import BaseModel


class Item(BaseModel):
    value: int | str


print(Item(value=1).value)     # 1
print(Item(value="1").value)   # '1'  (smart mode keeps exact type matches)
```

Pydantic's "smart" union mode first looks for an exact type match before trying coercion.

### Discriminated (tagged) unions

When each variant has a literal "type" field, tell Pydantic about it. Validation becomes faster, and error messages point at the correct variant instead of listing failures for every option.

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field, TypeAdapter


class Cat(BaseModel):
    pet_type: Literal["cat"]
    meows: int


class Dog(BaseModel):
    pet_type: Literal["dog"]
    barks: float


class Lizard(BaseModel):
    pet_type: Literal["lizard"]
    scales: bool


Pet = Annotated[Cat | Dog | Lizard, Field(discriminator="pet_type")]


class Owner(BaseModel):
    pets: list[Pet]


o = Owner.model_validate({"pets": [{"pet_type": "dog", "barks": 3}, {"pet_type": "cat", "meows": 1}]})
print([type(p).__name__ for p in o.pets])   # ['Dog', 'Cat']

pet = TypeAdapter(Pet).validate_python({"pet_type": "lizard", "scales": True})
```

This pattern is essential for event systems, webhook payloads and **LLM tool calls** (see §22).

---

## 15. Generic Models

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = 1
    size: int = 20


class Article(BaseModel):
    title: str


page = Page[Article].model_validate({"items": [{"title": "Hello"}], "total": 1})
print(page.items[0].title)   # Hello
```

On Python 3.12+ you can use the new syntax: `class Page[T](BaseModel): ...`.

Great for API envelopes: `ApiResponse[T]`, `Page[T]`, `Result[T]`.

---

## 16. `TypeAdapter`: Validating Without a Model

`TypeAdapter` brings full Pydantic validation to **any** type — lists, dicts, unions, `TypedDict`s — without defining a `BaseModel`.

```python
from pydantic import BaseModel, TypeAdapter


class User(BaseModel):
    id: int
    name: str


users_adapter = TypeAdapter(list[User])
users = users_adapter.validate_json('[{"id": 1, "name": "A"}, {"id": "2", "name": "B"}]')
print(users_adapter.dump_json(users))

int_map = TypeAdapter(dict[str, int])
print(int_map.validate_python({"a": "1", "b": 2}))   # {'a': 1, 'b': 2}
print(int_map.json_schema())
```

**Create adapters once** at module level — building one is relatively expensive; using it is cheap.

---

## 17. `@validate_call`: Validating Function Arguments

```python
from typing import Annotated
from pydantic import Field, ValidationError, validate_call


@validate_call
def repeat(text: str, times: Annotated[int, Field(gt=0, le=10)]) -> str:
    return text * times


print(repeat("ab", "3"))   # ababab  ("3" coerced to 3)

try:
    repeat("ab", 50)
except ValidationError as e:
    print(e.errors()[0]["msg"])   # Input should be less than or equal to 10
```

Add `@validate_call(validate_return=True)` to also validate the return value. Useful for public library functions and for the tool functions you expose to an LLM agent.

---

## 18. Dataclasses and `TypedDict`

### Pydantic dataclasses

If you prefer the dataclass style:

```python
from pydantic.dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int = 0


print(Point(x="5"))   # Point(x=5, y=0)
```

They validate on init but don't have `model_dump` etc.; use `TypeAdapter(Point).dump_python(p)` to serialize.

### `TypedDict`

Validate plain dicts while keeping them as dicts:

```python
from typing_extensions import NotRequired, TypedDict  # use typing_extensions on Python < 3.12
from pydantic import TypeAdapter


class MovieDict(TypedDict):
    title: str
    year: int
    rating: NotRequired[float]


movie = TypeAdapter(MovieDict).validate_python({"title": "Arrival", "year": "2016"})
print(movie, type(movie))   # {'title': 'Arrival', 'year': 2016} <class 'dict'>
```

### Which to choose?

| Use | When |
|---|---|
| `BaseModel` | Default choice. Richest API (dump, copy, schema, config). |
| `@pydantic.dataclasses.dataclass` | You want dataclass semantics or are adding validation to existing dataclasses. |
| `TypedDict` + `TypeAdapter` | You need plain dicts (e.g. passing to libraries expecting dicts), or zero object overhead. |

---

## 19. Settings Management with `pydantic-settings`

`BaseSettings` reads values from environment variables, `.env` files and secrets directories, then validates them like any model.

```python
from pydantic import Field, SecretStr, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    url: PostgresDsn = "postgresql://user:pass@localhost:5432/app"
    pool_size: int = 5


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",            # APP_DEBUG, APP_OPENAI_API_KEY, ...
        env_nested_delimiter="__",    # APP_DB__POOL_SIZE=10
        extra="ignore",
    )

    debug: bool = False
    environment: str = "dev"
    openai_api_key: SecretStr = SecretStr("")
    allowed_origins: list[str] = ["http://localhost:3000"]   # set as JSON: '["https://a.com"]'
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)


settings = Settings()
```

`.env` example:

```dotenv
APP_DEBUG=true
APP_ENVIRONMENT=prod
APP_OPENAI_API_KEY=sk-...
APP_DB__POOL_SIZE=20
APP_ALLOWED_ORIGINS=["https://app.example.com"]
```

**Priority order** (highest wins): init kwargs → environment variables → `.env` file → secrets dir → field defaults.

### Cache it

```python
from functools import lru_cache


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

In FastAPI, inject it with `Depends(get_settings)`; in tests, override the dependency or call `get_settings.cache_clear()`.

**Best practices**

- Wrap every secret in `SecretStr` so it never shows up in logs or tracebacks.
- Fail fast: instantiate settings at startup so misconfiguration crashes the deploy, not the first request.
- Commit a `.env.example`, never `.env`.

---

## 20. JSON Schema Generation

```python
import json
from typing import Literal
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Search the knowledge base."""

    query: str = Field(description="Natural-language search query", examples=["pydantic validators"])
    top_k: int = Field(default=5, ge=1, le=50)
    mode: Literal["semantic", "keyword", "hybrid"] = "hybrid"


print(json.dumps(SearchQuery.model_json_schema(), indent=2))
```

The class docstring becomes the schema `description`, and every `Field(description=...)` lands on its property. These schemas power:

- FastAPI's OpenAPI / Swagger docs
- LLM function/tool calling definitions
- Frontend form generation and contract tests

Use `model_json_schema(mode="serialization")` to describe the *output* shape (includes computed fields, respects serialization aliases).

---

## 21. Pydantic with FastAPI

FastAPI uses Pydantic for request bodies, query params, responses and docs. A clean pattern is **separate schemas per direction**:

```python
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field

app = FastAPI()


class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


DB: dict[int, dict] = {}


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate) -> UserOut:
    user_id = len(DB) + 1
    record = {**payload.model_dump(exclude={"password"}), "id": user_id, "created_at": datetime.now()}
    DB[user_id] = record
    return UserOut.model_validate(record)


@app.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, patch: UserUpdate) -> UserOut:
    if user_id not in DB:
        raise HTTPException(404, "User not found")
    DB[user_id].update(patch.model_dump(exclude_unset=True))
    return UserOut.model_validate(DB[user_id])
```

Why this works:

- `UserCreate` accepts the password; `UserOut` can never leak it.
- `response_model` filters the output even if you accidentally return extra fields.
- `extra="forbid"` turns client typos into clear `422` errors.
- `exclude_unset=True` makes PATCH update only what the client sent.

---

## 22. Pydantic for LLM and AI Engineering

LLM output is the definition of untrusted input. Pydantic is the de facto standard for **structured outputs** across the AI ecosystem — the OpenAI and Anthropic SDKs, LangChain, LlamaIndex, CrewAI, Instructor and PydanticAI all build on it.

### 22.1 Define the output contract

```python
from typing import Literal
from pydantic import BaseModel, Field


class ExtractedJob(BaseModel):
    """Structured information extracted from a job posting."""

    title: str = Field(description="Job title as written in the posting")
    company: str
    country: str = Field(description="ISO 3166-1 alpha-2 country code, e.g. 'DE', 'NL'")
    remote: Literal["onsite", "hybrid", "remote"]
    salary_min_eur: int | None = Field(default=None, ge=0, description="Annual minimum in EUR, if stated")
    skills: list[str] = Field(default_factory=list, max_length=20)
    visa_sponsorship: bool | None = Field(default=None, description="null if the posting does not say")
```

Descriptions matter: they become part of the schema the model sees, so write them as instructions.

### 22.2 Validate-and-retry loop

```python
from pydantic import ValidationError


def call_llm(prompt: str) -> str:
    """Placeholder for your LLM client call returning raw JSON text."""
    return '{"title": "AI Engineer", "company": "Acme", "country": "NL", "remote": "hybrid", "skills": ["python"]}'


def extract_job(posting: str, max_retries: int = 2) -> ExtractedJob:
    schema = ExtractedJob.model_json_schema()
    prompt = f"Extract the job as JSON matching this schema:\n{schema}\n\nPosting:\n{posting}"

    for attempt in range(max_retries + 1):
        raw = call_llm(prompt)
        try:
            return ExtractedJob.model_validate_json(raw)
        except ValidationError as e:
            if attempt == max_retries:
                raise
            # Feed the precise errors back so the model can self-correct
            prompt += f"\n\nYour previous answer was invalid:\n{e.json()}\nReturn corrected JSON only."
    raise RuntimeError("unreachable")


print(extract_job("We're hiring an AI Engineer in Amsterdam..."))
```

### 22.3 Tool calling with discriminated unions

Model every tool's arguments as a variant, and route the LLM's choice safely:

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field, TypeAdapter


class WebSearch(BaseModel):
    tool: Literal["web_search"]
    query: str


class GetWeather(BaseModel):
    tool: Literal["get_weather"]
    city: str
    unit: Literal["c", "f"] = "c"


class SendEmail(BaseModel):
    tool: Literal["send_email"]
    to: str
    subject: str
    body: str


ToolCall = Annotated[WebSearch | GetWeather | SendEmail, Field(discriminator="tool")]
tool_adapter = TypeAdapter(ToolCall)


def dispatch(raw_json: str) -> str:
    call = tool_adapter.validate_json(raw_json)
    match call:
        case WebSearch(query=q):
            return f"searching for {q!r}"
        case GetWeather(city=c, unit=u):
            return f"weather in {c} ({u})"
        case SendEmail():
            return "email requires human confirmation"   # gate side effects!


print(dispatch('{"tool": "get_weather", "city": "Berlin"}'))
```

Generate the tool definitions straight from the models:

```python
tools = [
    {
        "name": m.model_fields["tool"].annotation.__args__[0],
        "description": m.__doc__ or "",
        "input_schema": m.model_json_schema(),
    }
    for m in (WebSearch, GetWeather, SendEmail)
]
```

### 22.4 With the Anthropic and OpenAI SDKs

Both SDKs accept Pydantic models directly for structured outputs; check the current docs for the exact method names, as these APIs evolve quickly. The general shape:

```python
# OpenAI (sketch)
# completion = client.chat.completions.parse(model=..., messages=..., response_format=ExtractedJob)
# job = completion.choices[0].message.parsed

# Anthropic (sketch) — pass ExtractedJob.model_json_schema() as a tool's input_schema,
# then validate the returned tool_use input:
# job = ExtractedJob.model_validate(tool_use_block.input)
```

### 22.5 RAG and agent state

```python
from datetime import datetime
from pydantic import BaseModel, Field


class Chunk(BaseModel):
    id: str
    text: str
    source: str
    page: int | None = None
    score: float = Field(ge=0, le=1)


class RetrievalResult(BaseModel):
    query: str
    chunks: list[Chunk]
    retrieved_at: datetime = Field(default_factory=datetime.now)

    def as_context(self, max_chars: int = 4000) -> str:
        out, used = [], 0
        for c in sorted(self.chunks, key=lambda c: c.score, reverse=True):
            block = f"[{c.source} p.{c.page}] {c.text}"
            if used + len(block) > max_chars:
                break
            out.append(block)
            used += len(block)
        return "\n\n".join(out)


class AgentState(BaseModel):
    goal: str
    steps_taken: list[str] = []
    scratchpad: dict[str, str] = {}
    done: bool = False
```

Typed state makes agents easier to checkpoint (`model_dump_json`), resume (`model_validate_json`) and debug.

### 22.6 AI-specific tips

- **Make "unknown" representable.** Use `X | None` with a description like "null if not stated" — otherwise the model is pressured to hallucinate a value.
- **Use `Literal` / `Enum`** for categories so the model can't invent new labels.
- **Keep schemas shallow and small.** Deeply nested, huge schemas degrade output quality.
- **Validate business rules** with validators (e.g. `salary_max >= salary_min`) — the model will occasionally get them wrong.
- **Never trust tool arguments for side effects.** Validate, then authorize, then execute.

---

## 23. Performance Tips

1. **Use `model_validate_json`** on raw JSON instead of `json.loads` + `model_validate`.
2. **Reuse `TypeAdapter`s** — create them once at import time.
3. **Prefer discriminated unions** over plain unions with many members.
4. **Prefer `Annotated` constraints** (`Field(gt=0)`) over Python validators — constraints run in Rust.
5. **Avoid `mode="wrap"` validators** on hot paths; they're the slowest kind.
6. **Use `model_construct()`** to skip validation for data you *already trust* (e.g. rows you just wrote yourself):

   ```python
   fast = User.model_construct(id=1, name="trusted")   # no validation at all!
   ```

7. **Use `TypedDict`** instead of nested models when you don't need model instances.
8. **Choose `list` / `dict`** over abstract `Sequence` / `Mapping` where possible — concrete types validate faster.

---

## 24. Migrating from v1 to v2

| Pydantic v1 | Pydantic v2 |
|---|---|
| `class Config:` | `model_config = ConfigDict(...)` |
| `orm_mode = True` | `from_attributes=True` |
| `allow_population_by_field_name` | `populate_by_name` |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `.parse_obj(d)` | `.model_validate(d)` |
| `.parse_raw(s)` | `.model_validate_json(s)` |
| `.from_orm(o)` | `.model_validate(o)` (with `from_attributes`) |
| `.copy(update=...)` | `.model_copy(update=...)` |
| `.schema()` | `.model_json_schema()` |
| `.construct()` | `.model_construct()` |
| `.__fields__` | `.model_fields` |
| `@validator` | `@field_validator` |
| `@root_validator` | `@model_validator` |
| `each_item=True` | validate the item type with `Annotated[..., AfterValidator(...)]` |
| `const=True` | `Literal[...]` |
| `regex=` | `pattern=` |
| `min_items` / `max_items` | `min_length` / `max_length` |
| `parse_obj_as(T, x)` | `TypeAdapter(T).validate_python(x)` |
| `BaseSettings` in `pydantic` | `BaseSettings` in `pydantic-settings` |

Behavioural changes to watch for:

- `Optional[X]` **without a default is now required** (it just allows `None`). Add `= None` to make it optional.
- int → str coercion is gone: passing `123` to a `str` field fails.
- Validators must be `@classmethod`s.

Use the official tool to automate most of it:

```bash
pip install bump-pydantic
bump-pydantic my_package/
```

`from pydantic import v1` still exposes the old API if you need a gradual migration.

---

## 25. Common Pitfalls

**1. Assuming mutation is validated**

```python
from pydantic import BaseModel, ConfigDict


class A(BaseModel):
    n: int


a = A(n=1)
a.n = "not an int"   # no error! Use validate_assignment=True to catch this
```

**2. `Optional` without a default**

```python
class B(BaseModel):
    x: int | None        # REQUIRED (may be None)
    y: int | None = None # truly optional
```

**3. Silently dropped extra fields**

The default `extra="ignore"` means a misspelt key just disappears. Use `extra="forbid"` for request bodies.

**4. `model_copy(update=...)` skips validation**

Validate the merged data instead: `A.model_validate({**a.model_dump(), **changes})`.

**5. `model_construct()` on untrusted data**

It bypasses all checks. Only use it for data you produced yourself.

**6. Leaking secrets**

Plain `str` passwords show up in logs and `repr`. Use `SecretStr`, or `Field(repr=False, exclude=True)`.

**7. Forgetting `@classmethod` on validators**

v2 requires it for `@field_validator` and `mode="before"` / `"wrap"` model validators.

**8. Field names shadowing `BaseModel` attributes**

Avoid naming fields `model_*`, `dict`, `json`, `copy`, `schema`. Use an alias if the external key collides.

**9. Expensive validators doing I/O**

Don't hit the database or network inside validators. Pass precomputed data in via `context`.

---

## 26. Cheat Sheet

```python
from typing import Annotated, Literal
from pydantic import (
    BaseModel, ConfigDict, Field, TypeAdapter, ValidationError,
    field_validator, model_validator, computed_field,
    field_serializer, validate_call, SecretStr, EmailStr, HttpUrl,
)

# ---- Define
class M(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    a: int = Field(gt=0)
    b: str | None = None
    c: list[str] = []
    kind: Literal["x", "y"] = "x"

# ---- Create
M(a=1)
M.model_validate({"a": 1})
M.model_validate_json('{"a": 1}')
M.model_construct(a=1)            # no validation

# ---- Export
m = M(a=1)
m.model_dump()
m.model_dump(mode="json", exclude_none=True, by_alias=True)
m.model_dump_json(indent=2)
m.model_copy(update={"a": 2})
M.model_json_schema()

# ---- Introspect
M.model_fields                     # dict of FieldInfo
m.model_fields_set                 # fields explicitly set

# ---- Validate anything
TypeAdapter(list[int]).validate_python(["1", 2])

# ---- Errors
try:
    M(a=-1)
except ValidationError as e:
    e.errors(); e.json(); e.error_count()
```

---

## Further Reading

- Official docs: <https://docs.pydantic.dev>
- pydantic-settings: <https://docs.pydantic.dev/latest/concepts/pydantic_settings/>
- Migration guide: <https://docs.pydantic.dev/latest/migration/>
- FastAPI: <https://fastapi.tiangolo.com>
- PydanticAI (agent framework from the Pydantic team): <https://ai.pydantic.dev>

---

*Contributions and corrections welcome — open an issue or PR.*
