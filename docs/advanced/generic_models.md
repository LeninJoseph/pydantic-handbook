# Generic Models

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = 1
    size: int = 20


class Article(BaseModel):
    title: str


page = Page[Article].model_validate({"items": [{"title": "Hello"}], "total": 1})
print(page.items[0].title)   # Hello
```

On Python 3.12+ you can use the new syntax: `class Page[T](BaseModel): ...`.

Great for API envelopes: `ApiResponse[T]`, `Page[T]`, `Result[T]`.
