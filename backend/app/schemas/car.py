from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CarImageOut(BaseModel):
    url: str
    alt: str | None = None
    attribution: str | None = None
    license_name: str | None = None
    source_url: str | None = None


class CarOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    brand: str
    model: str
    trim: str | None
    year: int
    price_cny: Decimal
    range_km: int | None
    fuel_consumption_l_100km: Decimal | None = None
    battery_kwh: Decimal | None
    power_kw: int | None
    drivetrain: str | None
    category: str | None = None
    engine_type: str | None = None
    engine_cc: int | None = None
    fuel_type: str | None = None
    torque_nm: int | None = None
    acceleration_0_100_s: Decimal | None = None
    max_speed_kmh: int | None = None
    seats: int | None = None
    doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    wheelbase_mm: int | None = None
    advantages: str | None = None
    specification_source: str | None = None
    price_usd: Decimal | None = None
    price_tjs: Decimal | None = None
    price_note: str | None = None
    price_source: str | None = None
    transmission: str | None = None
    mileage_km: int | None = None
    exterior_color: str | None = None
    equipment: str | None = None
    specifications: str | None = None
    is_demo: bool = False
    availability: str
    localized_title: str | None = None
    localized_description: str | None = None
    images: list[str] = Field(default_factory=list)
    image_details: list[CarImageOut] = Field(default_factory=list)
