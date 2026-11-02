from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class QuoteRequest(BaseModel):
    price_cny: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    car_id: int | None = Field(default=None, gt=0)


class QuoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    car_id: int | None = None
    created_at: datetime
    currency: str = "TJS"
    price_cny: Decimal
    cny_to_tjs: Decimal
    customs_rate: Decimal
    car_tjs: Decimal
    shipping_tjs: Decimal
    customs_tjs: Decimal
    customs_basis: str
    additional_tjs: Decimal
    paperwork_tjs: Decimal
    total_tjs: Decimal
    effective_on: date
    tariff_name: str
