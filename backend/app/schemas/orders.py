from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


OrderStatus = Literal["requested", "confirmed", "sourcing", "purchased", "in_transit", "customs", "ready_for_delivery", "delivered", "cancelled"]


class OrderCreate(BaseModel):
    car_id: int
    customer_note: str | None = Field(default=None, max_length=2000)


class OrderStatusChange(BaseModel):
    status: OrderStatus
    public_note: str | None = Field(default=None, max_length=2000)
    internal_note: str | None = Field(default=None, max_length=4000)


class OrderEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    status: str | None
    public_note: str | None
    created_at: datetime


class OrderCarOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    brand: str
    model: str
    year: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    status: str
    customer_note: str | None
    car: OrderCarOut
    events: list[OrderEventOut]
    created_at: datetime
    updated_at: datetime


class StaffOrderEventOut(OrderEventOut):
    internal_note: str | None


class StaffCustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email_normalized: str
    phone: str | None


class StaffOrderOut(OrderOut):
    customer_id: int
    customer: StaffCustomerOut
    events: list[StaffOrderEventOut]


class NotificationOut(BaseModel):
    id: int
    order_id: int
    order_number: str
    status: OrderStatus | None
    public_note: str | None
    created_at: datetime
    read_at: datetime | None


class NotificationReadOut(BaseModel):
    updated: int


class OrderDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    byte_size: int | None
    visible_to_customer: bool
    created_at: datetime
