from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.security.roles import AccessRole


def validate_bcrypt_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password cannot be longer than 72 bytes")

    return password


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)
    role: AccessRole
    department: str | None = Field(default=None, max_length=100)

    _validate_password = field_validator("password")(validate_bcrypt_password)

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        normalized_name = name.strip()

        if len(normalized_name) < 2:
            raise ValueError("Name must be at least 2 characters")

        return normalized_name


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: AccessRole | None = None
    department: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    department: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
