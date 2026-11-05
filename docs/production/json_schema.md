# JSON Schema Generation

```python
import json
from typing import Literal
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Search the knowledge base."""

    query: str = Field(description="Natural-language search query", examples=["pydantic validators"])
    top_k: int = Field(default=5, ge=1, le=50)
    mode: Literal["semantic", "keyword", "hybrid"] = "hybrid"


print(json.dumps(SearchQuery.model_json_schema(), indent=2))
```

The class docstring becomes the schema `description`, and every `Field(description=...)` lands on its property. These schemas power:

- FastAPI's OpenAPI / Swagger docs
- LLM function/tool calling definitions
- Frontend form generation and contract tests

Use `model_json_schema(mode="serialization")` to describe the *output* shape (includes computed fields, respects serialization aliases).
