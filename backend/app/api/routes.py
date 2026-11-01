from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.db.session import get_db
from app.models import Car, PricingTariff
from app.schemas.car import CarOut
from app.schemas.pricing import QuoteOut, QuoteRequest
from app.services.pricing import Tariff, calculate_quote

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": "configured" if settings.database_url else "not_configured"}


@router.get("/cars", response_model=list[CarOut])
def list_cars(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    brand: str | None = Query(default=None, max_length=80),
    min_price_cny: Decimal | None = Query(default=None, ge=0),
    max_price_cny: Decimal | None = Query(default=None, ge=0),
    min_range_km: int | None = Query(default=None, ge=0),
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[CarOut]:
    statement = select(Car).options(selectinload(Car.images)).where(Car.published.is_(True))
    if q:
        term = f"%{q.strip()}%"
        statement = statement.where(or_(Car.brand.ilike(term), Car.model.ilike(term), Car.trim.ilike(term)))
    if brand:
        statement = statement.where(Car.brand.ilike(brand.strip()))
    if min_price_cny is not None:
        statement = statement.where(Car.price_cny >= min_price_cny)
    if max_price_cny is not None:
        statement = statement.where(Car.price_cny <= max_price_cny)
    if min_range_km is not None:
        statement = statement.where(Car.range_km >= min_range_km)
    cars = db.scalars(statement.order_by(Car.brand, Car.model).limit(limit).offset(offset)).all()
    return [CarOut.model_validate({**{key: getattr(car, key) for key in CarOut.model_fields if key != "images"}, "images": [image.url for image in car.images]}) for car in cars]


@router.post("/quotes", response_model=QuoteOut)
def quote(request: QuoteRequest, db: Session = Depends(get_db)) -> QuoteOut:
    tariff = db.scalar(select(PricingTariff).where(PricingTariff.active.is_(True), PricingTariff.effective_on <= date.today()).order_by(PricingTariff.effective_on.desc()))
    if tariff is None:
        raise HTTPException(status_code=503, detail="No current pricing tariff is configured")
    config = Tariff(
        name=tariff.name,
        effective_on=tariff.effective_on,
        cny_to_tjs=tariff.cny_to_tjs,
        shipping_tjs=tariff.shipping_tjs,
        customs_rate=tariff.customs_rate,
        customs_basis=tariff.customs_basis,
        additional_tjs=tariff.additional_tjs,
        paperwork_tjs=tariff.paperwork_tjs,
    )
    try:
        return QuoteOut(**calculate_quote(request.price_cny, config))
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
