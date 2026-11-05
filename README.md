# Pydantic Handbook

A practical, example-driven guide to **Pydantic v2**, from your first model to settings management, FastAPI integration and structured outputs for LLM / AI engineering.

**📖 Read it online: https://leninjoseph.github.io/pydantic-handbook/**

## Contents

| Section | Topics |
|---|---|
| Basics | Models, fields & constraints, validation errors, strict vs lax mode, nested models |
| Advanced | Validators, computed fields, serialization, aliases, `ConfigDict`, `Annotated` types, discriminated unions, generics, `TypeAdapter`, `@validate_call`, dataclasses & `TypedDict` |
| Production | `pydantic-settings`, JSON Schema, FastAPI patterns, performance |
| AI Engineering | Structured LLM outputs, validate-and-retry, tool calling, RAG & agent state |
| Reference | v1 → v2 migration, common pitfalls, cheat sheet |
| Interview Questions | 28 common Pydantic interview questions with answers |

## How to test locally

### Pre-reqs

1. Install Python 3.11+.

2. Create and activate a virtual environment in the cloned repo:

```
python3 -m venv venv
source venv/bin/activate
```

3. Install MkDocs and requirements:

```
pip install -r requirements.txt
```

4. Start the server:

```
mkdocs serve -a 0.0.0.0:8000
```

5. Browse the site at http://localhost:8000

### Check the code examples

Every Python example in `docs/` is executed in CI. To run them locally:

```
pip install -r requirements-examples.txt
python scripts/check_examples.py docs
```

## Deploy

Pushing to `main` runs the examples and then deploys the site to GitHub Pages automatically (`.github/workflows/deploy.yml`).

To deploy manually:

```
mkdocs gh-deploy
```
