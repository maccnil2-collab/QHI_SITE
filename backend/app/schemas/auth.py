from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


Locale = Literal["ru", "tg", "en"]


class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=5, max_length=254)
    password: SecretStr = Field(min_length=12, max_length=128)
    full_name: str = Field(min_length=1, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    preferred_locale: Locale = "ru"

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if value.count("@") != 1:
            raise ValueError("Enter a valid email address")
        local, domain = value.split("@")
        if not local or "." not in domain or domain.startswith(".") or domain.endswith(".") or any(ch.isspace() for ch in value):
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("full_name")
    @classmethod
    def nonempty_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value.strip()


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    password: SecretStr = Field(min_length=1, max_length=128)


class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if value.count("@") != 1:
            raise ValueError("Enter a valid email address")
        local, domain = value.split("@")
        if not local or "." not in domain or domain.startswith(".") or domain.endswith(".") or any(ch.isspace() for ch in value):
            raise ValueError("Enter a valid email address")
        return value


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=32, max_length=128)
    new_password: SecretStr = Field(min_length=12, max_length=128)


class PasswordResetRequestOut(BaseModel):
    accepted: bool
    message: str
    test_token: str | None = None


class PasswordResetConfirmOut(BaseModel):
    updated: bool


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str | None = Field(default=None, min_length=1, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    preferred_locale: Locale | None = None

    @field_validator("full_name")
    @classmethod
    def nonempty_name(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Name cannot be empty")
        return value.strip() if value is not None else None


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email_normalized: str
    full_name: str
    phone: str | None
    preferred_locale: str
    role: str
    email_verified: bool


class AuthResponse(BaseModel):
    expires_at: datetime
    csrf_token: str
    customer: CustomerOut


class CustomerSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    expires_at: datetime
    current: bool
