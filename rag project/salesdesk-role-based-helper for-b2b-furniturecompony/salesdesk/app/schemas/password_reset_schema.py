from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.schemas.user_schema import validate_bcrypt_password


class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr


class PasswordResetVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    otp: str = Field(pattern=r"^\d{6}$")


class PasswordResetVerifyResponse(BaseModel):
    reset_token: str


class PasswordResetConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reset_token: str
    password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)

    _validate_password = field_validator(
        "password",
        "confirm_password",
    )(validate_bcrypt_password)

    @model_validator(mode="after")
    def passwords_must_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")

        return self


class MessageResponse(BaseModel):
    message: str
