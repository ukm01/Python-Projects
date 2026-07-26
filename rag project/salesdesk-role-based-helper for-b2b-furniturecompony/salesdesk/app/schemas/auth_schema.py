from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.schemas.user_schema import validate_bcrypt_password


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str

    _validate_password = field_validator("password")(validate_bcrypt_password)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict
