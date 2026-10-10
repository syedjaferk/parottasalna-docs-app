from pydantic import BaseModel, field_validator


class SignupRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("username must not contain spaces")
        return v
