# Common Pitfalls

## 1. Assuming mutation is validated

```python
from pydantic import BaseModel


class A(BaseModel):
    n: int


a = A(n=1)
a.n = "not an int"   # no error! Use validate_assignment=True to catch this
```

## 2. `Optional` without a default

```python
from pydantic import BaseModel


class B(BaseModel):
    x: int | None        # REQUIRED (may be None)
    y: int | None = None # truly optional
```

## 3. Silently dropped extra fields

The default `extra="ignore"` means a misspelt key just disappears. Use `extra="forbid"` for request bodies.

## 4. `model_copy(update=...)` skips validation

Validate the merged data instead: `A.model_validate({**a.model_dump(), **changes})`.

## 5. `model_construct()` on untrusted data

It bypasses all checks. Only use it for data you produced yourself.

## 6. Leaking secrets

Plain `str` passwords show up in logs and `repr`. Use `SecretStr`, or `Field(repr=False, exclude=True)`.

## 7. Forgetting `@classmethod` on validators

v2 requires it for `@field_validator` and `mode="before"` / `"wrap"` model validators.

## 8. Field names shadowing `BaseModel` attributes

Avoid naming fields `model_*`, `dict`, `json`, `copy`, `schema`. Use an alias if the external key collides.

## 9. Expensive validators doing I/O

Don't hit the database or network inside validators. Pass precomputed data in via `context`.
