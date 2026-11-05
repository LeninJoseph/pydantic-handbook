# Strict vs Lax Mode

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
