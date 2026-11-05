# Pydantic Interview Questions

Common questions asked in Python backend and AI engineering interviews. Each answer is short enough to say out loud. Answers start collapsed, so you can test yourself first.

---

## Fundamentals

??? question "1. What is Pydantic and why would you use it?"
    Pydantic is a runtime data validation and parsing library driven by Python type hints. You declare the shape of your data as a model, and Pydantic validates input against it. It coerces compatible values and raises a structured `ValidationError` when the input is invalid. It also serializes models to dicts and JSON and generates JSON Schema.

    You use it at system **boundaries**, wherever untrusted data enters: API requests, config, environment variables, message queues and LLM outputs.

??? question "2. What changed between Pydantic v1 and v2?"
    - The core was rewritten in **Rust** (`pydantic-core`), which makes v2 roughly 5–50× faster.
    - The methods were renamed: `.dict()` → `.model_dump()`, `.parse_obj()` → `.model_validate()`, `.json()` → `.model_dump_json()`.
    - `class Config` became `model_config = ConfigDict(...)`.
    - `@validator` / `@root_validator` became `@field_validator` / `@model_validator`.
    - `Optional[X]` with no default is now **required**.
    - `BaseSettings` moved to the separate `pydantic-settings` package.
    - New tools were added: `TypeAdapter`, `@computed_field`, strict mode and better discriminated unions.

??? question "3. Is Pydantic a replacement for mypy?"
    No. Pydantic validates data at **runtime**, while mypy and pyright check code **statically** before it runs. They complement each other. Pydantic ships a mypy plugin so the two agree on model signatures.

??? question "4. What's the difference between lax mode and strict mode?"
    Lax mode is the default. In lax mode Pydantic coerces sensible inputs, so `"42"` becomes `42` for an `int` field and `"true"` becomes `True` for a `bool`. Strict mode rejects any value that isn't already the right type.

    You can enable strict mode per model (`ConfigDict(strict=True)`), per field (`StrictInt`, `Field(strict=True)`) or per call (`model_validate(data, strict=True)`).

    ```python
    from pydantic import BaseModel, ConfigDict, ValidationError


    class M(BaseModel):
        model_config = ConfigDict(strict=True)
        n: int


    try:
        M(n="1")
    except ValidationError as e:
        print(e.errors()[0]["type"])  # int_type
    ```

??? question "5. How do you make a field optional?"
    Give it a default. `x: int | None` is **required** but may be `None`. `x: int | None = None` is genuinely optional.

??? question "6. Is it safe to use a mutable default like `tags: list[str] = []`?"
    Yes. Unlike a plain Python class or function signature, Pydantic deep-copies defaults for each instance. For computed defaults, use `Field(default_factory=...)`.

---

## Validation

??? question "7. What are the four validator modes?"
    | Mode | When it runs | Typical use |
    |---|---|---|
    | `after` (default) | After Pydantic's type validation | Business rules on typed values |
    | `before` | Before type validation, on the raw input | Normalising messy input (e.g. CSV → list) |
    | `wrap` | Around Pydantic's validation, with a `handler` | Fallbacks, logging, catching errors |
    | `plain` | Instead of Pydantic's validation | Fully custom parsing |

??? question "8. `field_validator` vs `model_validator`: when do you use each?"
    Use `@field_validator` for rules about a **single field**, such as "username is alphanumeric". Use `@model_validator(mode="after")` for **cross-field** rules, such as "end_date is after start_date" or "the two passwords match". A `mode="before"` model validator can reshape the raw input before any field is validated.

??? question "9. How do you pass runtime data (like the current user or allowed values) into a validator?"
    Use **validation context**. Call `Model.model_validate(data, context={...})` and read `info.context` inside a validator that accepts `info: ValidationInfo`. That way validators never need globals or database calls.

??? question "10. Is an attribute re-validated when I assign to it after creation?"
    Not by default. Set `ConfigDict(validate_assignment=True)` to re-validate on assignment, or `frozen=True` to make the model immutable.

??? question "11. What does a `ValidationError` contain?"
    It contains **every** error, not just the first. Each entry in `e.errors()` has these keys:

    - `loc`: the path to the failing field, e.g. `('items', 2, 'price')`
    - `type`: a stable error code, e.g. `greater_than`
    - `msg`: a human-readable message
    - `input`: the value that failed

    `e.json()` gives the same as JSON, which is handy for API error responses.

??? question "12. How do you reuse the same constraint across many models?"
    Define an `Annotated` alias once and use it everywhere:

    ```python
    from typing import Annotated
    from pydantic import BaseModel, Field, StringConstraints

    Username = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, min_length=3)]
    Percentage = Annotated[float, Field(ge=0, le=100)]


    class Profile(BaseModel):
        username: Username
        completion: Percentage
    ```

---

## Serialization & Config

??? question "13. What's the difference between `model_dump()` and `model_dump(mode='json')`?"
    `model_dump()` returns Python objects, so a `datetime` stays a `datetime`. `mode="json"` returns only JSON-compatible types, so a `datetime` becomes an ISO string and a `UUID` becomes a string. `model_dump_json()` goes straight to a JSON string and is faster.

??? question "14. How would you implement a PATCH endpoint with Pydantic?"
    Make every field optional, then use `model_dump(exclude_unset=True)`. That returns only the fields the client actually sent, so `None` values the client didn't send never overwrite stored data.

??? question "15. What does `extra='forbid'` do, and why use it?"
    It makes unknown keys raise an error instead of being silently ignored (the default). For request bodies, this turns client typos like `"emial"` into a clear 422 instead of a silent data bug.

??? question "16. How do you convert between camelCase JSON and snake_case Python?"
    Set `ConfigDict(alias_generator=to_camel, populate_by_name=True)`, using `pydantic.alias_generators.to_camel`. Input then accepts camelCase, and `model_dump(by_alias=True)` outputs camelCase. With `populate_by_name=True`, Python code can still use the snake_case names.

??? question "17. How do you build a Pydantic model from an ORM object?"
    Set `ConfigDict(from_attributes=True)`, then call `Model.model_validate(orm_obj)`. Pydantic reads the object's attributes. Only fields declared on the model are included, which keeps columns like `password_hash` out of responses.

??? question "18. How do you keep secrets out of logs?"
    Use the `SecretStr` type. It shows as `**********` in `repr`, `str` and dumps, and you read the real value with `.get_secret_value()`. Alternatively, use `Field(repr=False, exclude=True)`.

---

## Advanced Types

??? question "19. What is a discriminated union and why is it better than a plain union?"
    It's a union where every variant has a `Literal` "tag" field, such as `type: Literal["cat"]`. You declare it with `Field(discriminator="type")`. Pydantic reads the tag and validates against the one matching variant. This is faster than trying each variant, and the errors refer only to that variant. It's the standard pattern for webhooks, event streams and LLM tool calls.

??? question "20. What is `TypeAdapter` for?"
    It runs Pydantic validation and serialization on **any** type that isn't a `BaseModel`, such as `list[User]`, `dict[str, int]`, unions or `TypedDict`s. You create it once and reuse it: `TypeAdapter(list[User]).validate_json(raw)`. It replaces v1's `parse_obj_as`.

??? question "21. When would you choose `TypedDict` or a Pydantic dataclass over `BaseModel`?"
    - **`BaseModel`** is the default, with the richest API: dump, copy, schema and config.
    - **Pydantic dataclass**: you want dataclass semantics, or you're adding validation to existing dataclasses.
    - **`TypedDict` + `TypeAdapter`**: you need the result to stay a plain `dict`, or you want minimal overhead.

??? question "22. What does `model_construct()` do and when is it dangerous?"
    It creates an instance **without any validation**, which is fast. It's only safe for data you already trust, such as data you just produced yourself. Using it on external input defeats the purpose of Pydantic.

---

## Settings, FastAPI & Performance

??? question "23. How does `pydantic-settings` resolve a value?"
    In priority order: init kwargs, then environment variables, then the `.env` file, then the secrets directory, then field defaults. `env_prefix` namespaces the variables (e.g. `APP_`). `env_nested_delimiter="__"` maps `APP_DB__POOL_SIZE` to `settings.db.pool_size`. Wrap the settings in `@lru_cache` so they're loaded once.

??? question "24. Why have separate `UserCreate`, `UserUpdate` and `UserOut` schemas in FastAPI?"
    Each direction has different rules:

    - **Create** accepts a password.
    - **Update** makes every field optional, for PATCH.
    - **Out** must never expose the password and adds server fields like `id` and `created_at`.

    One shared model either leaks data or forces awkward optionality. FastAPI's `response_model` also filters the output to the declared schema.

??? question "25. How do you make Pydantic validation faster?"
    - Use `model_validate_json` on raw JSON instead of `json.loads` followed by validation.
    - Build each `TypeAdapter` once, at module level.
    - Prefer discriminated unions to plain unions.
    - Prefer declarative constraints (`Field(gt=0)`), which run in Rust, over Python validators.
    - Avoid `wrap` validators on hot paths.
    - Use `model_construct` only for trusted data.

---

## AI Engineering

??? question "26. How would you get reliable structured output from an LLM?"
    1. Define a Pydantic model as the output contract, with a `description` on each field. The descriptions become instructions in the schema.
    2. Pass `model_json_schema()` to the LLM as a tool schema or response format.
    3. Validate the response with `model_validate_json`.
    4. On a `ValidationError`, send `e.json()` back to the model and retry a bounded number of times.
    5. Enforce business rules with validators, because the model will sometimes violate them.

??? question "27. How do you design schemas so LLMs hallucinate less?"
    - Make "unknown" representable: use `X | None` with a description like "null if not stated".
    - Use `Literal` or `Enum` for categories so the model can't invent labels.
    - Keep schemas small and shallow.
    - Write field descriptions as instructions to the model.

??? question "28. How would you safely route LLM tool calls?"
    Model each tool's arguments as one variant of a discriminated union keyed on the tool name, and validate with a `TypeAdapter`. Then dispatch with `match`. Validation only proves the arguments are well-formed, not that the action is allowed. Authorize before any side effect, and require human confirmation for destructive actions like sending email or making payments.

---

!!! tip "Practice"
    For every question, try writing the code from memory, then compare it with the relevant page in this handbook.
