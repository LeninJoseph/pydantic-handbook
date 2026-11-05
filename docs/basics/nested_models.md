# Nested Models and Collections

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

## Self-referencing models

```python
from __future__ import annotations
from pydantic import BaseModel


class TreeNode(BaseModel):
    value: int
    children: list[TreeNode] = []


tree = TreeNode(value=1, children=[{"value": 2}, {"value": 3, "children": [{"value": 4}]}])
print(tree.children[1].children[0].value)  # 4
```
