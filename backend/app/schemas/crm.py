from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.auth import Locale


LeadStatus = Literal["new", "contacted", "qualified", "converted", "lost"]
InteractionKind = Literal["call", "email", "meeting", "note"]


class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    email: str | None = Field(default=None, min_length=5, max_length=254)
    phone: str | None = Field(default=None, min_length=5, max_length=32)
    preferred_locale: Locale = "ru"
    message: str | None = Field(default=None, max_length=4000)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name is required")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().lower()
        if value.count("@") != 1 or any(ch.isspace() for ch in value) or "." not in value.split("@", 1)[1]:
            raise ValueError("Enter a valid email address")
        return value

    @model_validator(mode="after")
    def require_contact_channel(self):
        if not self.email and not self.phone:
            raise ValueError("Provide an email address or phone number")
        return self


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int | None
    assigned_manager_id: int | None
    name: str
    email: str | None
    phone: str | None
    preferred_locale: str
    source: str
    status: str
    message: str | None
    created_at: datetime
    updated_at: datetime


class LeadReceipt(BaseModel):
    id: int
    status: str = "received"


class LeadUpdate(BaseModel):
    status: LeadStatus | None = None
    assigned_manager_id: int | None = None


class InteractionCreate(BaseModel):
    kind: InteractionKind
    summary: str = Field(min_length=1, max_length=4000)

    @field_validator("summary")
    @classmethod
    def nonempty_summary(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Interaction summary cannot be empty")
        return value


class InteractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    actor_id: int | None
    kind: str
    summary: str
    created_at: datetime


class CRMOverview(BaseModel):
    leads_by_status: dict[str, int]
    orders_by_status: dict[str, int]
