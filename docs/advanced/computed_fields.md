# Computed Fields

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
