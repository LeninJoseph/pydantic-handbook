# Advanced

Customising how Pydantic validates, transforms and serializes data.

## Topics

- [Validators](validators.md): field validators, model validators, the four modes, and validation context
- [Computed Fields](computed_fields.md)
- [Serialization](serialization.md): `model_dump`, `model_dump_json`, PATCH patterns and custom serializers
- [Aliases](aliases.md): camelCase ↔ snake_case, `AliasChoices` and `AliasPath`
- [Model Config](model_config.md): `ConfigDict` options you'll actually use
- [Annotated Types](annotated_types.md): reusable constraints and validators
- [Unions](unions.md): smart unions and discriminated (tagged) unions
- [Generic Models](generic_models.md): `Page[T]`, `ApiResponse[T]`
- [TypeAdapter](type_adapter.md): validating any type without a model
- [@validate_call](validate_call.md): validating function arguments
- [Dataclasses and TypedDict](dataclasses_typeddict.md)
