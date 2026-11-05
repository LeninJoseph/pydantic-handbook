# Performance Tips

1. **Use `model_validate_json`** on raw JSON instead of `json.loads` + `model_validate`.
2. **Reuse `TypeAdapter`s** — create them once at import time.
3. **Prefer discriminated unions** over plain unions with many members.
4. **Prefer `Annotated` constraints** (`Field(gt=0)`) over Python validators — constraints run in Rust.
5. **Avoid `mode="wrap"` validators** on hot paths; they're the slowest kind.
6. **Use `model_construct()`** to skip validation for data you *already trust* (e.g. rows you just wrote yourself):

   ```python
   from pydantic import BaseModel


   class User(BaseModel):
       id: int
       name: str


   fast = User.model_construct(id=1, name="trusted")   # no validation at all!
   ```

7. **Use `TypedDict`** instead of nested models when you don't need model instances.
8. **Choose `list` / `dict`** over abstract `Sequence` / `Mapping` where possible — concrete types validate faster.
