# Migrating from v1 to v2

| Pydantic v1 | Pydantic v2 |
|---|---|
| `class Config:` | `model_config = ConfigDict(...)` |
| `orm_mode = True` | `from_attributes=True` |
| `allow_population_by_field_name` | `populate_by_name` |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `.parse_obj(d)` | `.model_validate(d)` |
| `.parse_raw(s)` | `.model_validate_json(s)` |
| `.from_orm(o)` | `.model_validate(o)` (with `from_attributes`) |
| `.copy(update=...)` | `.model_copy(update=...)` |
| `.schema()` | `.model_json_schema()` |
| `.construct()` | `.model_construct()` |
| `.__fields__` | `.model_fields` |
| `@validator` | `@field_validator` |
| `@root_validator` | `@model_validator` |
| `each_item=True` | validate the item type with `Annotated[..., AfterValidator(...)]` |
| `const=True` | `Literal[...]` |
| `regex=` | `pattern=` |
| `min_items` / `max_items` | `min_length` / `max_length` |
| `parse_obj_as(T, x)` | `TypeAdapter(T).validate_python(x)` |
| `BaseSettings` in `pydantic` | `BaseSettings` in `pydantic-settings` |

Behavioural changes to watch for:

- `Optional[X]` **without a default is now required** (it just allows `None`). Add `= None` to make it optional.
- int → str coercion is gone: passing `123` to a `str` field fails.
- Validators must be `@classmethod`s.

Use the official tool to automate most of it:

```bash
pip install bump-pydantic
bump-pydantic my_package/
```

`from pydantic import v1` still exposes the old API if you need a gradual migration.
