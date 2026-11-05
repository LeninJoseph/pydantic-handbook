# Pydantic with FastAPI

FastAPI uses Pydantic for request bodies, query params, responses and docs. A clean pattern is **separate schemas per direction**:

```python
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field

app = FastAPI()


class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


DB: dict[int, dict] = {}


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate) -> UserOut:
    user_id = len(DB) + 1
    record = {**payload.model_dump(exclude={"password"}), "id": user_id, "created_at": datetime.now()}
    DB[user_id] = record
    return UserOut.model_validate(record)


@app.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, patch: UserUpdate) -> UserOut:
    if user_id not in DB:
        raise HTTPException(404, "User not found")
    DB[user_id].update(patch.model_dump(exclude_unset=True))
    return UserOut.model_validate(DB[user_id])
```

Why this works:

- `UserCreate` accepts the password; `UserOut` can never leak it.
- `response_model` filters the output even if you accidentally return extra fields.
- `extra="forbid"` turns client typos into clear `422` errors.
- `exclude_unset=True` makes PATCH update only what the client sent.
