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
    battery_kwh: Decimal | None
    power_kw: int | None
    drivetrain: str | None
    availability: str
    images: list[str] = Field(default_factory=list)
