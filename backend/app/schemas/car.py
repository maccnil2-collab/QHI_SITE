from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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
