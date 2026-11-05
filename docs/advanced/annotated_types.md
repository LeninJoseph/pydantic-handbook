# Annotated Types and Reusable Constraints

`typing.Annotated` lets you package a type plus its constraints and validators into a reusable alias.

```python
from typing import Annotated
from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, StringConstraints

Username = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, min_length=3, max_length=30)]
Percentage = Annotated[float, Field(ge=0, le=100)]


def must_be_even(v: int) -> int:
    if v % 2:
        raise ValueError("must be even")
    return v


EvenInt = Annotated[int, AfterValidator(must_be_even)]
CommaList = Annotated[list[str], BeforeValidator(lambda v: v.split(",") if isinstance(v, str) else v)]


class Profile(BaseModel):
    username: Username
    completion: Percentage
    lucky_number: EvenInt
    skills: CommaList


print(Profile(username="  LENIN ", completion=87.5, lucky_number=4, skills="python,ai,fastapi"))
# username='lenin' completion=87.5 lucky_number=4 skills=['python', 'ai', 'fastapi']
```

This is the cleanest way to share validation logic across many models — far better than copy-pasting `@field_validator`s.
