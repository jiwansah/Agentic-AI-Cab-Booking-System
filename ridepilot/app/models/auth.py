# app/models/auth.py

from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator

class GuestResumeRequest(BaseModel):
    credential: str = Field(min_length=20, max_length=256)


class GuestForgetRequest(BaseModel):
    confirm: bool

class LoginRequest(BaseModel):
    identifier: str = Field(
        min_length=3,
        max_length=254,
    )
    password: str = Field(
        min_length=8,
        max_length=128,
    )

class RegisterRequest(BaseModel):
    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
    )
    email: EmailStr | None = None
    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("phone", mode="before")
    @classmethod
    def empty_phone_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value


    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value


    @model_validator(mode="after")
    def require_phone_or_email(self):
        if not self.phone and not self.email:
            raise ValueError(
                "Either phone or email is required"
            )
        return self


