---
hide:
  - navigation
  - toc
---

<div class="hb-hero" markdown>

# Pydantic Handbook

A practical, example-driven guide to **Pydantic v2**: the data validation library behind FastAPI, the OpenAI and Anthropic SDKs, LangChain, CrewAI and PydanticAI.

[Start learning :material-arrow-right:](basics/index.md){ .md-button .md-button--primary }
[Interview questions](interview/interview_questions.md){ .md-button }
[GitHub :fontawesome-brands-github:](https://github.com/LeninJoseph/pydantic-handbook){ .md-button }

</div>

## Explore the Handbook

<div class="grid cards" markdown>

-   :material-school-outline:{ .lg .middle } **Basics**

    ---

    Models, fields and constraints, validation errors, strict vs lax mode, nested models.

    [:octicons-arrow-right-24: Start here](basics/index.md)

-   :material-tune-variant:{ .lg .middle } **Advanced**

    ---

    Validators, serialization, aliases, `ConfigDict`, `Annotated` types, discriminated unions, generics, `TypeAdapter`.

    [:octicons-arrow-right-24: Go deeper](advanced/index.md)

-   :material-server-network:{ .lg .middle } **Production**

    ---

    `pydantic-settings`, JSON Schema, FastAPI request/response patterns and performance tips.

    [:octicons-arrow-right-24: Ship it](production/index.md)

-   :material-robot-outline:{ .lg .middle } **AI Engineering**

    ---

    Structured LLM outputs, validate-and-retry loops, tool calling, RAG and agent state.

    [:octicons-arrow-right-24: Build with LLMs](ai_engineering/index.md)

-   :material-book-open-page-variant-outline:{ .lg .middle } **Reference**

    ---

    v1 → v2 migration table, common pitfalls and a one-page cheat sheet.

    [:octicons-arrow-right-24: Look it up](reference/index.md)

-   :material-account-tie-voice-outline:{ .lg .middle } **Interview Questions**

    ---

    28 common Pydantic questions with concise answers you can say out loud.

    [:octicons-arrow-right-24: Practise](interview/interview_questions.md)

</div>

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

!!! info "Versions"
    Written and tested against **Pydantic 2.13** and **pydantic-settings 2.16** on Python 3.11+.
    Every code example on this site is executed in CI.

## How to Use This Guide

1. New to Pydantic? Follow the **Basics** tab in order.
2. Already using it? Jump to **Advanced** or **Production**.
3. Building with LLMs? Go straight to **AI Engineering**.
4. Preparing for an interview? Use **Interview Questions** and the **Cheat Sheet**.
