from pydantic import BaseModel, Field


class AuthUserIn(BaseModel):
    allows_write_to_pm: bool | None = Field(default=None)
    first_name: str
    id: int | None = Field(default=None)
    language_code: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    username: str | None = Field(default=None)


class AuthUserOut(BaseModel):
    name: str | None
    tg_id: int | None
    lang: str | None
    net: str | None
    address: str | None
