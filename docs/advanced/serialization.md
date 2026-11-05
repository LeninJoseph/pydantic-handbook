# Serialization: `model_dump` and `model_dump_json`

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

## Copying with changes

```python
updated = e.model_copy(update={"title": "Relaunch"})
```

`model_copy(update=...)` does **not** validate the update — validate first if the data is untrusted.

## Custom serializers

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
