# Custom Validators

## Field validators

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

## Validator modes

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

## Model validators (cross-field checks)

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

## Validation context

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
