# Cheat Sheet

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
