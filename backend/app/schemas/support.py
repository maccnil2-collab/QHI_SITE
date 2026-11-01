from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

SupportCategory = Literal["general", "vehicle", "technical", "complaint", "suggestion", "feedback"]
TicketStatus = Literal["open", "in_progress", "resolved", "closed"]

class TicketCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    email: str = Field(min_length=5, max_length=254)
    category: SupportCategory
    subject: str = Field(min_length=2, max_length=180)
    message: str = Field(min_length=10, max_length=5000)
    locale: Literal["ru", "tg", "en"] = "en"
    @field_validator("name", "subject", "message")
    @classmethod
    def strip_nonempty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if value.count("@") != 1 or any(c.isspace() for c in value) or "." not in value.split("@", 1)[1]:
            raise ValueError("Enter a valid email address")
        return value

class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    note: str | None = Field(default=None, max_length=4000)

class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_number: str
    name: str
    email: str
    category: str
    subject: str
    message: str
    locale: str
    status: str
    created_at: datetime
    updated_at: datetime
