# Your First Model

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

## Three ways to build a model

```python
User(id=1, name="A")                                 # keyword args
User.model_validate({"id": 1, "name": "A"})          # from a dict
User.model_validate_json('{"id": 1, "name": "A"}')   # from a JSON string (fastest path)
```

Prefer `model_validate_json` when you already have raw JSON — it parses and validates in one Rust pass instead of `json.loads` + validate.
