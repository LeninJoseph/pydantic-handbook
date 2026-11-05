# Unions and Discriminated Unions

## Plain unions

```python
from pydantic import BaseModel


class Item(BaseModel):
    value: int | str


print(Item(value=1).value)     # 1
print(Item(value="1").value)   # '1'  (smart mode keeps exact type matches)
```

Pydantic's "smart" union mode first looks for an exact type match before trying coercion.

## Discriminated (tagged) unions

When each variant has a literal "type" field, tell Pydantic about it. Validation becomes faster, and error messages point at the correct variant instead of listing failures for every option.

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field, TypeAdapter


class Cat(BaseModel):
    pet_type: Literal["cat"]
    meows: int


class Dog(BaseModel):
    pet_type: Literal["dog"]
    barks: float


class Lizard(BaseModel):
    pet_type: Literal["lizard"]
    scales: bool


Pet = Annotated[Cat | Dog | Lizard, Field(discriminator="pet_type")]


class Owner(BaseModel):
    pets: list[Pet]


o = Owner.model_validate({"pets": [{"pet_type": "dog", "barks": 3}, {"pet_type": "cat", "meows": 1}]})
print([type(p).__name__ for p in o.pets])   # ['Dog', 'Cat']

pet = TypeAdapter(Pet).validate_python({"pet_type": "lizard", "scales": True})
```

This pattern is essential for event systems, webhook payloads and **LLM tool calls** (see [LLM Structured Outputs](../ai_engineering/llm_structured_outputs.md)).
