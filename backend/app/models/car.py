from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    brand: Mapped[str] = mapped_column(String(80), index=True)
    model: Mapped[str] = mapped_column(String(100), index=True)
    trim: Mapped[str | None] = mapped_column(String(120), nullable=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    price_cny: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    range_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel_consumption_l_100km: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    battery_kwh: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    power_kw: Mapped[int | None] = mapped_column(Integer, nullable=True)
    drivetrain: Mapped[str | None] = mapped_column(String(32), nullable=True)
    category: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    engine_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    engine_cc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel_type: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    torque_nm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    acceleration_0_100_s: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    max_speed_kmh: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    doors: Mapped[int | None] = mapped_column(Integer, nullable=True)
    length_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wheelbase_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    advantages: Mapped[str | None] = mapped_column(Text, nullable=True)
    specification_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_usd: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    price_tjs: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    price_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    transmission: Mapped[str | None] = mapped_column(String(40), nullable=True)
    mileage_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    exterior_color: Mapped[str | None] = mapped_column(String(80), nullable=True)
    equipment: Mapped[str | None] = mapped_column(Text, nullable=True)
    specifications: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    availability: Mapped[str] = mapped_column(String(24), default="on_request")
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    images: Mapped[list["CarImage"]] = relationship(back_populates="car", cascade="all, delete-orphan")
    translations: Mapped[list["CarTranslation"]] = relationship(back_populates="car", cascade="all, delete-orphan")


class CarImage(Base):
    __tablename__ = "car_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(Text)
    alt: Mapped[str | None] = mapped_column(String(240), nullable=True)
    attribution: Mapped[str | None] = mapped_column(String(500), nullable=True)
    license_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    car: Mapped[Car] = relationship(back_populates="images")


class CarTranslation(Base):
    __tablename__ = "car_translations"
    __table_args__ = (UniqueConstraint("car_id", "locale", name="uq_car_translation_locale"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(2), index=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    car: Mapped[Car] = relationship(back_populates="translations")
