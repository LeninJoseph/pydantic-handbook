# Aliases

Aliases bridge naming conventions — e.g. camelCase JSON to snake_case Python.

```python
from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class GitHubUser(BaseModel):
    login: str
    avatar: str = Field(alias="avatar_url")                                  # one external name
    full_name: str = Field(validation_alias=AliasChoices("name", "fullName"))  # accept several
    city: str = Field(validation_alias=AliasPath("location", "city"))       # pull from nested path


u = GitHubUser.model_validate({
    "login": "leninjoseph",
    "avatar_url": "https://x/y.png",
    "fullName": "Lenin Joseph",
    "location": {"city": "Chennai"},
})
print(u.full_name, u.city)


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    first_name: str
    last_name: str


m = CamelModel.model_validate({"firstName": "Lenin", "lastName": "Joseph"})
print(m.model_dump(by_alias=True))   # {'firstName': 'Lenin', 'lastName': 'Joseph'}
CamelModel(first_name="A", last_name="B")   # works because populate_by_name=True
```

- `alias` — used for both validation and serialization.
- `validation_alias` — input only.
- `serialization_alias` — output only (needs `by_alias=True`).
