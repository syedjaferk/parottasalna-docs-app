from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    username: str
    email: str
    is_active: bool = True  # simple default
    bio: str | None = None  # optional field
    tags: list[str] = Field(
        default_factory=list
    )  # mutable default (never use `= []` directly)


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    age: int = Field(ge=13, le=120, description="User age in years")
    email: EmailStr  # built-in email format validation
    password: str = Field(min_length=8)
