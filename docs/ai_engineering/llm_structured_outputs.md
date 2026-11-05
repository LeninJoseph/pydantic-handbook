# Pydantic for LLM and AI Engineering

LLM output is the definition of untrusted input. Pydantic is the de facto standard for **structured outputs** across the AI ecosystem — the OpenAI and Anthropic SDKs, LangChain, LlamaIndex, CrewAI, Instructor and PydanticAI all build on it.

## Define the output contract

```python
from typing import Literal
from pydantic import BaseModel, Field


class ExtractedJob(BaseModel):
    """Structured information extracted from a job posting."""

    title: str = Field(description="Job title as written in the posting")
    company: str
    country: str = Field(description="ISO 3166-1 alpha-2 country code, e.g. 'DE', 'NL'")
    remote: Literal["onsite", "hybrid", "remote"]
    salary_min_eur: int | None = Field(default=None, ge=0, description="Annual minimum in EUR, if stated")
    skills: list[str] = Field(default_factory=list, max_length=20)
    visa_sponsorship: bool | None = Field(default=None, description="null if the posting does not say")
```

Descriptions matter: they become part of the schema the model sees, so write them as instructions.

## Validate-and-retry loop

```python
from pydantic import ValidationError


def call_llm(prompt: str) -> str:
    """Placeholder for your LLM client call returning raw JSON text."""
    return '{"title": "AI Engineer", "company": "Acme", "country": "NL", "remote": "hybrid", "skills": ["python"]}'


def extract_job(posting: str, max_retries: int = 2) -> ExtractedJob:
    schema = ExtractedJob.model_json_schema()
    prompt = f"Extract the job as JSON matching this schema:\n{schema}\n\nPosting:\n{posting}"

    for attempt in range(max_retries + 1):
        raw = call_llm(prompt)
        try:
            return ExtractedJob.model_validate_json(raw)
        except ValidationError as e:
            if attempt == max_retries:
                raise
            # Feed the precise errors back so the model can self-correct
            prompt += f"\n\nYour previous answer was invalid:\n{e.json()}\nReturn corrected JSON only."
    raise RuntimeError("unreachable")


print(extract_job("We're hiring an AI Engineer in Amsterdam..."))
```

## Tool calling with discriminated unions

Model every tool's arguments as a variant, and route the LLM's choice safely:

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field, TypeAdapter


class WebSearch(BaseModel):
    tool: Literal["web_search"]
    query: str


class GetWeather(BaseModel):
    tool: Literal["get_weather"]
    city: str
    unit: Literal["c", "f"] = "c"


class SendEmail(BaseModel):
    tool: Literal["send_email"]
    to: str
    subject: str
    body: str


ToolCall = Annotated[WebSearch | GetWeather | SendEmail, Field(discriminator="tool")]
tool_adapter = TypeAdapter(ToolCall)


def dispatch(raw_json: str) -> str:
    call = tool_adapter.validate_json(raw_json)
    match call:
        case WebSearch(query=q):
            return f"searching for {q!r}"
        case GetWeather(city=c, unit=u):
            return f"weather in {c} ({u})"
        case SendEmail():
            return "email requires human confirmation"   # gate side effects!


print(dispatch('{"tool": "get_weather", "city": "Berlin"}'))
```

Generate the tool definitions straight from the models:

```python
tools = [
    {
        "name": m.model_fields["tool"].annotation.__args__[0],
        "description": m.__doc__ or "",
        "input_schema": m.model_json_schema(),
    }
    for m in (WebSearch, GetWeather, SendEmail)
]
```

## With the Anthropic and OpenAI SDKs

Both SDKs accept Pydantic models directly for structured outputs; check the current docs for the exact method names, as these APIs evolve quickly. The general shape:

```python
# OpenAI (sketch)
# completion = client.chat.completions.parse(model=..., messages=..., response_format=ExtractedJob)
# job = completion.choices[0].message.parsed

# Anthropic (sketch) — pass ExtractedJob.model_json_schema() as a tool's input_schema,
# then validate the returned tool_use input:
# job = ExtractedJob.model_validate(tool_use_block.input)
```

## RAG and agent state

```python
from datetime import datetime
from pydantic import BaseModel, Field


class Chunk(BaseModel):
    id: str
    text: str
    source: str
    page: int | None = None
    score: float = Field(ge=0, le=1)


class RetrievalResult(BaseModel):
    query: str
    chunks: list[Chunk]
    retrieved_at: datetime = Field(default_factory=datetime.now)

    def as_context(self, max_chars: int = 4000) -> str:
        out, used = [], 0
        for c in sorted(self.chunks, key=lambda c: c.score, reverse=True):
            block = f"[{c.source} p.{c.page}] {c.text}"
            if used + len(block) > max_chars:
                break
            out.append(block)
            used += len(block)
        return "\n\n".join(out)


class AgentState(BaseModel):
    goal: str
    steps_taken: list[str] = []
    scratchpad: dict[str, str] = {}
    done: bool = False
```

Typed state makes agents easier to checkpoint (`model_dump_json`), resume (`model_validate_json`) and debug.

## AI-specific tips

- **Make "unknown" representable.** Use `X | None` with a description like "null if not stated" — otherwise the model is pressured to hallucinate a value.
- **Use `Literal` / `Enum`** for categories so the model can't invent new labels.
- **Keep schemas shallow and small.** Deeply nested, huge schemas degrade output quality.
- **Validate business rules** with validators (e.g. `salary_max >= salary_min`) — the model will occasionally get them wrong.
- **Never trust tool arguments for side effects.** Validate, then authorize, then execute.
