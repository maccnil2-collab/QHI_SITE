from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PricingTariff(Base):
    __tablename__ = "pricing_tariffs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    currency: Mapped[str] = mapped_column(String(3), default="TJS")
    cny_to_tjs: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    shipping_tjs: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    customs_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    customs_basis: Mapped[str | None] = mapped_column(String(32), nullable=True)
    additional_tjs: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    paperwork_tjs: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    effective_on: Mapped[date]
    source_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

# Database-enforced single active tariff, including concurrent admin requests.
Index("uq_pricing_tariffs_one_active", PricingTariff.active, unique=True, postgresql_where=PricingTariff.active.is_(True))
