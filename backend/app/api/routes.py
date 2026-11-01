from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import and_, or_, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.core.auth import get_optional_customer
from app.core.config import settings
from app.core.rate_limit import SlidingWindowLimiter
from app.db.session import engine, get_db
from app.models import Car, CarTranslation, Customer, PricingTariff, PriceQuote
from app.schemas.car import CarOut
from app.schemas.pricing import QuoteOut, QuoteRequest
from app.services.pricing import Tariff, calculate_quote

router = APIRouter()
quote_limiter = SlidingWindowLimiter(max_requests=10, window_seconds=60)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": "configured" if settings.database_url else "not_configured"}


@router.get("/ready", responses={503: {"description": "Database is unavailable"}})
def readiness() -> dict[str, str]:
    if engine is None:
        raise HTTPException(status_code=503, detail="Service is not ready")
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Service is not ready") from None
    return {"status": "ready", "database": "connected"}


@router.get("/cars", response_model=list[CarOut])
def list_cars(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    locale: Literal["ru", "tg", "en"] = "ru",
    brand: str | None = Query(default=None, max_length=80),
    min_price_cny: Decimal | None = Query(default=None, ge=0),
    max_price_cny: Decimal | None = Query(default=None, ge=0),
    min_range_km: int | None = Query(default=None, ge=0),
    category: str | None = Query(default=None, max_length=40),
    sort: Literal["price_asc", "price_desc", "year_desc", "range_desc", "name"] = "name",
    include_demo: bool = True,
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[CarOut]:
    statement = select(Car).options(selectinload(Car.images), selectinload(Car.translations)).where(Car.published.is_(True))
    if q:
        term = f"%{q.strip()}%"
        statement = statement.where(or_(Car.brand.ilike(term), Car.model.ilike(term), Car.trim.ilike(term), Car.translations.any(and_(CarTranslation.locale == locale, CarTranslation.title.ilike(term)))))
    if brand:
        statement = statement.where(Car.brand.ilike(brand.strip()))
    if min_price_cny is not None:
        statement = statement.where(Car.price_cny >= min_price_cny)
    if max_price_cny is not None:
        statement = statement.where(Car.price_cny <= max_price_cny)
    if min_range_km is not None:
        statement = statement.where(Car.range_km >= min_range_km)
    if category:
        statement = statement.where(Car.category == category)
    if not include_demo:
        statement = statement.where(Car.is_demo.is_(False))
    sort_column = {"price_asc": Car.price_cny.asc(), "price_desc": Car.price_cny.desc(), "year_desc": Car.year.desc(), "range_desc": Car.range_km.desc().nullslast(), "name": Car.brand.asc()}.get(sort)
    ordering = (sort_column, Car.model.asc()) if sort == "name" else (sort_column,)
    cars = db.scalars(statement.order_by(*ordering).limit(limit).offset(offset)).all()
    return [_car_output(car, locale) for car in cars]


def _car_output(car: Car, locale: str) -> CarOut:
    return CarOut.model_validate({
        **{key: getattr(car, key, CarOut.model_fields[key].default if CarOut.model_fields[key].default is not None else None) for key in CarOut.model_fields if key not in {"images", "localized_title", "localized_description"}},
        "localized_title": next((item.title for item in car.translations if item.locale == locale), f"{car.brand} {car.model}"),
        "localized_description": next((item.description for item in car.translations if item.locale == locale), None),
        "images": [image.url for image in car.images],
    })


@router.get("/cars/{slug}", response_model=CarOut)
def get_car(slug: str, locale: Literal["ru", "tg", "en"] = "ru", db: Session = Depends(get_db)) -> CarOut:
    car = db.scalar(
        select(Car)
        .options(selectinload(Car.images), selectinload(Car.translations))
        .where(Car.slug == slug, Car.published.is_(True))
    )
    if car is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return _car_output(car, locale)


@router.post("/quotes", response_model=QuoteOut)
def quote(data: QuoteRequest, request: Request, db: Session = Depends(get_db), customer: Customer | None = Depends(get_optional_customer)) -> QuoteOut:
    host = request.client.host if request.client else "unknown"
    quote_limiter.check(f"quote:{host}", db)
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
        result = calculate_quote(data.price_cny, config)
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    quote = PriceQuote(
        tariff_id=tariff.id,
        customer_id=customer.id if customer else None,
        tariff_name=tariff.name,
        effective_on=tariff.effective_on,
        currency=tariff.currency,
        price_cny=data.price_cny,
        cny_to_tjs=tariff.cny_to_tjs,
        shipping_tjs=tariff.shipping_tjs,
        customs_rate=tariff.customs_rate,
        customs_basis=tariff.customs_basis,
        additional_tjs=tariff.additional_tjs,
        paperwork_tjs=tariff.paperwork_tjs,
        car_tjs=result["car_tjs"],
        customs_tjs=result["customs_tjs"],
        total_tjs=result["total_tjs"],
    )
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return QuoteOut(id=quote.id, created_at=quote.created_at, currency=quote.currency, price_cny=quote.price_cny, cny_to_tjs=quote.cny_to_tjs, customs_rate=quote.customs_rate, **result)
