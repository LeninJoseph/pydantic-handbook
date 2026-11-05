# Dataclasses and `TypedDict`

## Pydantic dataclasses

If you prefer the dataclass style:

```python
from pydantic.dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int = 0


print(Point(x="5"))   # Point(x=5, y=0)
```

They validate on init but don't have `model_dump` etc.; use `TypeAdapter(Point).dump_python(p)` to serialize.

## `TypedDict`

Validate plain dicts while keeping them as dicts:

```python
from typing_extensions import NotRequired, TypedDict  # use typing_extensions on Python < 3.12
from pydantic import TypeAdapter


class MovieDict(TypedDict):
    title: str
    year: int
    rating: NotRequired[float]


movie = TypeAdapter(MovieDict).validate_python({"title": "Arrival", "year": "2016"})
print(movie, type(movie))   # {'title': 'Arrival', 'year': 2016} <class 'dict'>
```

## Which to choose?

| Use | When |
|---|---|
| `BaseModel` | Default choice. Richest API (dump, copy, schema, config). |
| `@pydantic.dataclasses.dataclass` | You want dataclass semantics or are adding validation to existing dataclasses. |
| `TypedDict` + `TypeAdapter` | You need plain dicts (e.g. passing to libraries expecting dicts), or zero object overhead. |
