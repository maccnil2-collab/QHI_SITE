from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


Locale = Literal["ru", "tg", "en"]
Availability = Literal["available", "on_request", "unavailable"]
CustomsBasis = Literal["vehicle_value", "vehicle_plus_shipping"]


class TranslationInput(BaseModel):
    locale: Locale
    title: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=10000)


class CarWrite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    slug: str = Field(min_length=2, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    brand: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=100)
    trim: str | None = Field(default=None, max_length=120)
    year: int = Field(ge=2000, le=2100)
    price_cny: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    range_km: int | None = Field(default=None, ge=0, le=3000)
    battery_kwh: Decimal | None = Field(default=None, ge=0, max_digits=7, decimal_places=2)
    power_kw: int | None = Field(default=None, ge=0, le=3000)
    drivetrain: str | None = Field(default=None, max_length=32)
    availability: Availability = "on_request"
    published: bool = False
    image_urls: list[HttpUrl] = Field(default_factory=list, max_length=20)
    translations: list[TranslationInput] = Field(default_factory=list, max_length=3)


class TariffWrite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=120)
    cny_to_tjs: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=6)
    shipping_tjs: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    customs_rate: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=6)
    customs_basis: CustomsBasis | None = None
    additional_tjs: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    paperwork_tjs: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    effective_on: date
    source_note: str | None = Field(default=None, max_length=500)

class TariffOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    currency: str
    cny_to_tjs: Decimal | None
    shipping_tjs: Decimal | None
    customs_rate: Decimal | None
    customs_basis: str | None
    additional_tjs: Decimal | None
    paperwork_tjs: Decimal | None
    effective_on: date
    source_note: str | None
    active: bool


class RoleChange(BaseModel):
    role: Literal["customer", "manager", "admin"]
