# `TypeAdapter`: Validating Without a Model

`TypeAdapter` brings full Pydantic validation to **any** type — lists, dicts, unions, `TypedDict`s — without defining a `BaseModel`.

```python
from pydantic import BaseModel, TypeAdapter


class User(BaseModel):
    id: int
    name: str


users_adapter = TypeAdapter(list[User])
users = users_adapter.validate_json('[{"id": 1, "name": "A"}, {"id": "2", "name": "B"}]')
print(users_adapter.dump_json(users))

int_map = TypeAdapter(dict[str, int])
print(int_map.validate_python({"a": "1", "b": 2}))   # {'a': 1, 'b': 2}
print(int_map.json_schema())
```

**Create adapters once** at module level — building one is relatively expensive; using it is cheap.
