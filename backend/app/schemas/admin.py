from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.schemas.car import CarOut


Locale = Literal["ru", "tg", "en"]
Availability = Literal["available", "on_request", "unavailable"]
CarCategory = Literal["sedan", "suv", "crossover", "sports", "electric", "premium", "economy", "family"]
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
    fuel_consumption_l_100km: Decimal | None = Field(default=None, gt=0, le=100, max_digits=5, decimal_places=2)
    battery_kwh: Decimal | None = Field(default=None, ge=0, max_digits=7, decimal_places=2)
    power_kw: int | None = Field(default=None, ge=0, le=3000)
    drivetrain: str | None = Field(default=None, max_length=32)
    category: CarCategory | None = None
    engine_type: str | None = Field(default=None, max_length=40)
    engine_cc: int | None = Field(default=None, ge=0, le=15000)
    transmission: str | None = Field(default=None, max_length=40)
    mileage_km: int | None = Field(default=None, ge=0, le=2000000)
    exterior_color: str | None = Field(default=None, max_length=80)
    equipment: str | None = Field(default=None, max_length=10000)
    specifications: str | None = Field(default=None, max_length=10000)
    is_demo: bool = False
    availability: Availability = "on_request"
    published: bool = False
    image_urls: list[HttpUrl] = Field(default_factory=list, max_length=20)
    translations: list[TranslationInput] = Field(min_length=3, max_length=3)

    @model_validator(mode="after")
    def require_all_locales(self):
        locales = {item.locale for item in self.translations}
        if locales != {"ru", "tg", "en"}:
            raise ValueError("Exactly one translation for each locale (ru, tg, en) is required")
        return self


class AdminCarOut(CarOut):
    published: bool
    translations: list[TranslationInput]


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
