# Model Configuration (`ConfigDict`)

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
