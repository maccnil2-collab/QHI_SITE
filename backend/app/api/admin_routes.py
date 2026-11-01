from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.admin_auth import require_admin
from app.db.session import get_db
from app.models import AuditEvent, Car, CarImage, CarTranslation, PricingTariff
from app.schemas.admin import CarWrite, TariffOut, TariffWrite
from app.schemas.car import CarOut

router = APIRouter(prefix="/admin", tags=["admin"])


def car_output(car: Car) -> CarOut:
    values = {key: getattr(car, key) for key in CarOut.model_fields if key != "images"}
    values["images"] = [image.url for image in sorted(car.images, key=lambda item: item.sort_order)]
    return CarOut.model_validate(values)


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
    car.translations.clear()
    car.images.extend(CarImage(url=str(url), sort_order=index) for index, url in enumerate(data.image_urls))
    car.translations.extend(CarTranslation(locale=item.locale, title=item.title, description=item.description) for item in data.translations)


@router.get("/cars", response_model=list[CarOut])
def admin_list_cars(actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> list[CarOut]:
    cars = db.scalars(select(Car).options(selectinload(Car.images)).order_by(Car.id)).all()
    return [car_output(car) for car in cars]


@router.post("/cars", response_model=CarOut, status_code=status.HTTP_201_CREATED)
def create_car(data: CarWrite, actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> CarOut:
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


@router.put("/cars/{car_id}", response_model=CarOut)
def update_car(car_id: int, data: CarWrite, actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> CarOut:
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
    db.commit()
    db.refresh(tariff)
    return tariff


@router.post("/tariffs/{tariff_id}/activate", response_model=TariffOut)
def activate_tariff(tariff_id: int, actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> PricingTariff:
    tariff = db.get(PricingTariff, tariff_id)
    if tariff is None:
        raise HTTPException(status_code=404, detail="Tariff not found")
    previous = db.scalars(select(PricingTariff).where(PricingTariff.active.is_(True))).all()
    db.execute(update(PricingTariff).values(active=False))
    for old in previous:
        if old.id != tariff.id:
            audit(db, actor, "deactivate", "pricing_tariff", old.id, {"name": old.name})
    tariff.active = True
    audit(db, actor, "activate", "pricing_tariff", tariff.id, tariff_audit_payload(tariff))
    db.commit()
    db.refresh(tariff)
    return tariff

@router.patch("/cars/{car_id}/publication", response_model=CarOut)
def set_car_publication(car_id: int, published: bool, actor: str = Depends(require_admin), db: Session = Depends(get_db)) -> CarOut:
    car = db.scalar(select(Car).options(selectinload(Car.images)).where(Car.id == car_id))
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    car.published = published
    audit(db, actor, "publish" if published else "unpublish", "car", car.id, {"slug": car.slug, "published": published})
    db.commit()
    db.refresh(car)
    return car_output(car)
