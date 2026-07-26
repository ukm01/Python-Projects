from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


def validate_bcrypt_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password cannot be longer than 72 bytes")

    return password


class AdminCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    email: EmailStr
    password: str
    department: str | None = "IT"

    _validate_password = field_validator("password")(validate_bcrypt_password)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    department: str | None
    is_active: bool

    class Config:
        from_attributes = True
