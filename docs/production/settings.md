# Settings Management with `pydantic-settings`

`BaseSettings` reads values from environment variables, `.env` files and secrets directories, then validates them like any model.

```python
from pydantic import Field, SecretStr, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    url: PostgresDsn = "postgresql://user:pass@localhost:5432/app"
    pool_size: int = 5


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",            # APP_DEBUG, APP_OPENAI_API_KEY, ...
        env_nested_delimiter="__",    # APP_DB__POOL_SIZE=10
        extra="ignore",
    )

    debug: bool = False
    environment: str = "dev"
    openai_api_key: SecretStr = SecretStr("")
    allowed_origins: list[str] = ["http://localhost:3000"]   # set as JSON: '["https://a.com"]'
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)


settings = Settings()
```

`.env` example:

```dotenv
APP_DEBUG=true
APP_ENVIRONMENT=prod
APP_OPENAI_API_KEY=sk-...
APP_DB__POOL_SIZE=20
APP_ALLOWED_ORIGINS=["https://app.example.com"]
```

**Priority order** (highest wins): init kwargs → environment variables → `.env` file → secrets dir → field defaults.

## Cache it

```python
from functools import lru_cache


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

In FastAPI, inject it with `Depends(get_settings)`; in tests, override the dependency or call `get_settings.cache_clear()`.

**Best practices**

- Wrap every secret in `SecretStr` so it never shows up in logs or tracebacks.
- Fail fast: instantiate settings at startup so misconfiguration crashes the deploy, not the first request.
- Commit a `.env.example`, never `.env`.
