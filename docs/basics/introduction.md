# What Pydantic Is (and Isn't)

Pydantic is a **data validation and parsing library** driven by Python type hints. You describe the shape of your data with ordinary annotations, and Pydantic:

- **Validates** incoming data against those types and constraints.
- **Coerces** compatible input into the declared type (e.g. `"42"` → `42`) unless you ask for strict mode.
- **Serializes** objects back into dicts and JSON.
- **Generates JSON Schema** describing the model.

The core validation engine (`pydantic-core`) is written in Rust, which makes v2 dramatically faster than v1.

What Pydantic is **not**:

- Not an ORM — it doesn't talk to databases (though it pairs well with SQLAlchemy and SQLModel).
- Not a static type checker — it validates at **runtime**. Use mypy/pyright alongside it.
- Not a guarantee once the object exists — by default, assigning an invalid value to an attribute after creation is *not* re-validated (see `validate_assignment`).

**Rule of thumb:** use Pydantic at the **boundaries** of your system — HTTP requests, config files, environment variables, message queues, LLM outputs — anywhere untrusted data enters.
