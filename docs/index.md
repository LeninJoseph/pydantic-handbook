# Pydantic Handbook

A practical, example-driven guide to **Pydantic v2**, the most widely used data validation library for Python.

Pydantic turns Python type hints into runtime validation, parsing and serialization. It powers FastAPI and the OpenAI and Anthropic SDKs, as well as LangChain, LlamaIndex, CrewAI and PydanticAI. That makes it a core skill for backend and AI engineering roles.

!!! info "Versions"
    Written and tested against **Pydantic 2.13** and **pydantic-settings 2.16** on Python 3.11+.
    Every code example on this site is executed in CI.

---

## What You'll Learn

| Section | Topics |
|---|---|
| [Basics](basics/index.md) | Models, fields and constraints, validation errors, strict vs lax mode, nested models |
| [Advanced](advanced/index.md) | Validators, computed fields, serialization, aliases, `ConfigDict`, `Annotated` types, discriminated unions, generics, `TypeAdapter`, `@validate_call` |
| [Production](production/index.md) | `pydantic-settings`, JSON Schema, FastAPI patterns, performance |
| [AI Engineering](ai_engineering/index.md) | Structured LLM outputs, validate-and-retry loops, tool calling, RAG and agent state |
| [Reference](reference/index.md) | v1 → v2 migration, common pitfalls, cheat sheet |
| [Interview Questions](interview/interview_questions.md) | Common Pydantic questions with concise answers |

---

## 60-Second Example

```python
from pydantic import BaseModel, Field, ValidationError


class User(BaseModel):
    id: int
    name: str = Field(min_length=1)
    email: str
    tags: list[str] = []


user = User.model_validate({"id": "42", "name": "Lenin", "email": "lenin@example.com"})
print(user.id)            # 42  (coerced from "42")
print(user.model_dump())  # {'id': 42, 'name': 'Lenin', 'email': 'lenin@example.com', 'tags': []}

try:
    User(id="abc", name="", email="x")
except ValidationError as e:
    print(e.error_count())  # 2
```

---

## How to Use This Guide

1. New to Pydantic? Follow the **Basics** tab in order.
2. Already using it? Jump to **Advanced** or **Production**.
3. Building with LLMs? Go straight to **AI Engineering**.
4. Preparing for an interview? Use the **Interview Questions** tab and the **Cheat Sheet**.
