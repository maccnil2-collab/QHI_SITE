from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TestPaymentRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=56, pattern=r"^[A-Za-z0-9._:-]+$")
    outcome: Literal["approved", "declined"]


class RefundRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=56, pattern=r"^[A-Za-z0-9._:-]+$")
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    note: str = Field(min_length=3, max_length=500)


class PaymentEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    amount: Decimal
    currency: str
    note: str | None
    created_at: datetime


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: str
    order_id: int
    provider: str
    amount: Decimal
    currency: str
    status: str
    created_at: datetime
    events: list[PaymentEventOut] = Field(default_factory=list)
