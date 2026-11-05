# AI Engineering

LLM output is untrusted input. Pydantic is the standard way to turn free-form model output into typed, validated data.

## Topics

- [LLM Structured Outputs](llm_structured_outputs.md):
    - Defining output contracts with descriptive fields
    - Validate-and-retry loops that feed errors back to the model
    - Tool calling with discriminated unions
    - Using Pydantic with the OpenAI and Anthropic SDKs
    - Typed RAG results and agent state
    - AI-specific schema design tips

## Where Pydantic Shows Up in the AI Stack

| Library | How it uses Pydantic |
|---|---|
| OpenAI / Anthropic SDKs | Response types; structured outputs from models |
| LangChain / LlamaIndex | Output parsers, tool schemas |
| CrewAI | Task outputs (`output_pydantic`), tool argument schemas |
| Instructor | Patches LLM clients to return validated models |
| PydanticAI | Agent framework built by the Pydantic team |
| FastAPI | Serving models behind typed APIs |
