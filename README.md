# Pydantic Handbook

A practical, example-driven guide to **Pydantic v2** — from your first model to settings management, FastAPI integration, and structured outputs for LLM / AI engineering.

**👉 [Read the handbook](HANDBOOK.md)**

## What's inside

| Part | Topics |
|---|---|
| Foundations | Models, fields & constraints, validation errors, strict vs lax mode, nested models |
| Customisation | Field & model validators, computed fields, serializers, aliases, `ConfigDict` |
| Advanced types | `Annotated` reusable types, discriminated unions, generic models, `TypeAdapter`, `@validate_call`, dataclasses & `TypedDict` |
| In production | `pydantic-settings`, JSON Schema, FastAPI patterns, performance tips |
| AI engineering | Structured LLM outputs, validate-and-retry loops, tool calling with tagged unions, RAG & agent state |
| Reference | v1 → v2 migration table, common pitfalls, cheat sheet |

## Every example runs

All 44 Python examples are executed in CI on Python 3.11–3.13:

```bash
pip install -r requirements.txt
python scripts/check_examples.py HANDBOOK.md
```

## Versions

Written against Pydantic **2.13** and pydantic-settings **2.16**.

## Contributing

Spotted an error or want a new section? Open an issue or a pull request.
