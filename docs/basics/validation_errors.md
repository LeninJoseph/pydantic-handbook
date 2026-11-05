# Validation Errors

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
