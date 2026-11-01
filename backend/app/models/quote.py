from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PriceQuote(Base):
    __tablename__ = "price_quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    tariff_id: Mapped[int] = mapped_column(ForeignKey("pricing_tariffs.id", ondelete="RESTRICT"), index=True)
    tariff_name: Mapped[str] = mapped_column(String(120))
    effective_on: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3), default="TJS")
    price_cny: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    cny_to_tjs: Mapped[Decimal] = mapped_column(Numeric(12, 6))
    shipping_tjs: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    customs_rate: Mapped[Decimal] = mapped_column(Numeric(8, 6))
    customs_basis: Mapped[str] = mapped_column(String(32))
    additional_tjs: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    paperwork_tjs: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    car_tjs: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    customs_tjs: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total_tjs: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
