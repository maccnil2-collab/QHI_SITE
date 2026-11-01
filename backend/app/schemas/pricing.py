from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class QuoteRequest(BaseModel):
    price_cny: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


class QuoteOut(BaseModel):
    currency: str = "TJS"
    car_tjs: Decimal
    shipping_tjs: Decimal
    customs_tjs: Decimal
    customs_basis: str
    additional_tjs: Decimal
    paperwork_tjs: Decimal
    total_tjs: Decimal
    effective_on: date
    tariff_name: str
