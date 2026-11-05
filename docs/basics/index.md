# Basics

The foundations of Pydantic: what it does, how to define models, and how validation behaves.

## Topics

- [Introduction](introduction.md): what Pydantic is, and where it fits in your system
- [Installation](installation.md)
- [Your First Model](first_model.md): defining models and the three ways to create them
- [Fields](fields.md): types, defaults, constraints and built-in types like `EmailStr` and `SecretStr`
- [Validation Errors](validation_errors.md): reading and using `ValidationError`
- [Strict vs Lax Mode](strict_mode.md): when Pydantic coerces types and when it refuses
- [Nested Models](nested_models.md): composition, collections and self-referencing models

## Key Idea

Use Pydantic at the **boundaries** of your system: HTTP requests, config files, environment variables, queues and LLM outputs. Anywhere untrusted data enters, describe its shape with a model and let Pydantic enforce it.
