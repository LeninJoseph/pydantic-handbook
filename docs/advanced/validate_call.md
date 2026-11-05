# `@validate_call`: Validating Function Arguments

```python
from typing import Annotated
from pydantic import Field, ValidationError, validate_call


@validate_call
def repeat(text: str, times: Annotated[int, Field(gt=0, le=10)]) -> str:
    return text * times


print(repeat("ab", "3"))   # ababab  ("3" coerced to 3)

try:
    repeat("ab", 50)
except ValidationError as e:
    print(e.errors()[0]["msg"])   # Input should be less than or equal to 10
```

Add `@validate_call(validate_return=True)` to also validate the return value. Useful for public library functions and for the tool functions you expose to an LLM agent.
