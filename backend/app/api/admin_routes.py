from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.admin_auth import require_admin
from app.db.session import get_db
from app.models import AuditEvent, Car, CarImage, CarTranslation, Customer, PricingTariff
from app.schemas.admin import AdminCarOut, CarWrite, RoleChange, TariffOut, TariffWrite
from app.schemas.car import CarOut
from app.schemas.auth import CustomerOut
from app.services.pricing import Tariff

router = APIRouter(prefix="/admin", tags=["admin"])


def car_output(car: Car) -> AdminCarOut:
    values = {key: getattr(car, key) for key in CarOut.model_fields if key not in {"images", "localized_title", "localized_description"}}
    values["images"] = [image.url for image in sorted(car.images, key=lambda item: item.sort_order)]
    values["published"] = car.published
    values["translations"] = [{"locale": item.locale, "title": item.title, "description": item.description} for item in car.translations]
    return AdminCarOut.model_validate(values)


def audit(db: Session, actor: str, action: str, entity: str, identifier: int | str, payload: dict) -> None:
    db.add(AuditEvent(actor=actor, action=action, entity_type=entity, entity_id=str(identifier), payload=payload))


def car_audit_payload(car: Car) -> dict:
    return {"slug": car.slug, "brand": car.brand, "model": car.model, "trim": car.trim, "year": car.year, "price_cny": str(car.price_cny), "availability": car.availability, "published": car.published}


def tariff_audit_payload(tariff: PricingTariff) -> dict:
    return {"name": tariff.name, "effective_on": tariff.effective_on.isoformat(), "cny_to_tjs": str(tariff.cny_to_tjs) if tariff.cny_to_tjs is not None else None, "shipping_tjs": str(tariff.shipping_tjs) if tariff.shipping_tjs is not None else None, "customs_rate": str(tariff.customs_rate) if tariff.customs_rate is not None else None, "customs_basis": tariff.customs_basis, "additional_tjs": str(tariff.additional_tjs) if tariff.additional_tjs is not None else None, "paperwork_tjs": str(tariff.paperwork_tjs) if tariff.paperwork_tjs is not None else None}


def apply_car(car: Car, data: CarWrite) -> None:
    for key in ("slug", "brand", "model", "trim", "year", "price_cny", "range_km", "battery_kwh", "power_kw", "drivetrain", "availability", "published"):
        setattr(car, key, getattr(data, key))
    car.images.clear()
    car.images.extend(CarImage(url=str(url), sort_order=index) for index, url in enumerate(data.image_urls))
    existing_translations = {item.locale: item for item in car.translations}
    submitted_locales = {item.locale for item in data.translations}
    for locale, translation in existing_translations.items():
        if locale not in submitted_locales:
            car.translations.remove(translation)
    for item in data.translations:
        translation = existing_translations.get(item.locale)
        if translation is None:
            car.translations.append(CarTranslation(locale=item.locale, title=item.title, description=item.description))
        else:
            translation.title = item.title
            translation.description = item.description


@router.get("/cars", response_model=list[AdminCarOut])
def admin_list_cars(actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> list[AdminCarOut]:
    cars = db.scalars(select(Car).options(selectinload(Car.images), selectinload(Car.translations)).order_by(Car.id)).all()
    return [car_output(car) for car in cars]


@router.post("/cars", response_model=AdminCarOut, status_code=status.HTTP_201_CREATED)
def create_car(data: CarWrite, actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> AdminCarOut:
    car = Car()
    apply_car(car, data)
    db.add(car)
    try:
        db.flush()
        audit(db, actor, "create", "car", car.id, car_audit_payload(car))
        db.commit()
        db.refresh(car)
        return car_output(car)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="A car with this slug already exists") from error


@router.put("/cars/{car_id}", response_model=AdminCarOut)
def update_car(car_id: int, data: CarWrite, actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> AdminCarOut:
    car = db.scalar(select(Car).options(selectinload(Car.images), selectinload(Car.translations)).where(Car.id == car_id))
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    apply_car(car, data)
    audit(db, actor, "update", "car", car.id, car_audit_payload(car))
    try:
        db.commit()
        db.refresh(car)
        return car_output(car)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="A car with this slug already exists") from error


@router.get("/tariffs", response_model=list[TariffOut])
def admin_list_tariffs(actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> list[TariffOut]:
    return list(db.scalars(select(PricingTariff).order_by(PricingTariff.effective_on.desc(), PricingTariff.id.desc())).all())


@router.post("/tariffs", response_model=TariffOut, status_code=status.HTTP_201_CREATED)
def create_tariff(data: TariffWrite, actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> PricingTariff:
    tariff = PricingTariff(**data.model_dump(), active=False)
    db.add(tariff)
    db.flush()
    audit(db, actor, "create", "pricing_tariff", tariff.id, {**tariff_audit_payload(tariff), "active": False})
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tariff could not be saved; retry the request") from error
    db.refresh(tariff)
    return tariff


@router.post("/tariffs/{tariff_id}/activate", response_model=TariffOut)
def activate_tariff(tariff_id: int, actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> PricingTariff:
    tariff = db.get(PricingTariff, tariff_id)
    if tariff is None:
        raise HTTPException(status_code=404, detail="Tariff not found")
    config = Tariff(tariff.name, tariff.effective_on, tariff.cny_to_tjs, tariff.shipping_tjs, tariff.customs_rate, tariff.customs_basis, tariff.additional_tjs, tariff.paperwork_tjs)
    missing = config.missing()
    if missing:
        raise HTTPException(status_code=422, detail=f"Cannot activate incomplete tariff: {', '.join(missing)}")
    previous = db.scalars(select(PricingTariff).where(PricingTariff.active.is_(True))).all()
    db.execute(update(PricingTariff).values(active=False))
    for old in previous:
        if old.id != tariff.id:
            audit(db, actor, "deactivate", "pricing_tariff", old.id, {"name": old.name})
    tariff.active = True
    audit(db, actor, "activate", "pricing_tariff", tariff.id, tariff_audit_payload(tariff))
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="Concurrent tariff activation; retry the request") from error
    db.refresh(tariff)
    return tariff

@router.patch("/cars/{car_id}/publication", response_model=AdminCarOut)
def set_car_publication(car_id: int, published: bool, actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> AdminCarOut:
    car = db.scalar(select(Car).options(selectinload(Car.images), selectinload(Car.translations)).where(Car.id == car_id))
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    car.published = published
    audit(db, actor, "publish" if published else "unpublish", "car", car.id, {"slug": car.slug, "published": published})
    db.commit()
    db.refresh(car)
    return car_output(car)


@router.get("/customers", response_model=list[CustomerOut])
def admin_list_customers(limit: int = Query(default=50, ge=1, le=100), offset: int = Query(default=0, ge=0), actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> list[CustomerOut]:
    customers = db.scalars(select(Customer).order_by(Customer.created_at.desc()).limit(limit).offset(offset)).all()
    return [CustomerOut.model_validate(customer) for customer in customers]


@router.patch("/customers/{customer_id}/role", response_model=CustomerOut)
def set_customer_role(customer_id: int, data: RoleChange, actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> CustomerOut:
    # Lock the active admin set to prevent concurrent requests removing its last member.
    active_admins = db.scalars(select(Customer).where(Customer.role == "admin", Customer.is_active.is_(True)).order_by(Customer.id).with_for_update()).all()
    customer = db.scalar(select(Customer).where(Customer.id == customer_id).with_for_update())
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    if customer.role == "admin" and customer.is_active and data.role != "admin" and len(active_admins) <= 1:
        raise HTTPException(status_code=409, detail="Cannot remove the last active administrator")
    previous_role = customer.role
    customer.role = data.role
    audit(db, actor, "role_change", "customer", customer.id, {"from": previous_role, "to": data.role})
    db.commit()
    db.refresh(customer)
    return CustomerOut.model_validate(customer)
