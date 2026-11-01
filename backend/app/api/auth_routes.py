from datetime import UTC, datetime
import secrets
from functools import lru_cache
from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.auth import AuthContext, get_auth_context, issue_session, require_staff
from app.core.passwords import hash_password, verify_password
from app.core.rate_limit import SlidingWindowLimiter
from app.db.session import get_db
from app.models import Car, CarImage, CarTranslation, Customer, CustomerComparisonItem, CustomerFavorite, CustomerSession, OrderEvent, PriceQuote, VehicleOrder
from app.schemas.auth import AuthResponse, CustomerOut, CustomerSessionOut, LoginRequest, ProfileUpdate, RegisterRequest
from app.schemas.car import CarOut
from app.schemas.customer import ComparisonUpdate, FavoriteStatus
from app.services.orders import transition_order
from app.schemas.orders import OrderCreate, OrderOut, OrderStatusChange, StaffOrderOut
from app.schemas.pricing import QuoteOut

router = APIRouter(prefix="/auth", tags=["auth"])
register_limiter = SlidingWindowLimiter(max_requests=5, window_seconds=60)
login_limiter = SlidingWindowLimiter(max_requests=8, window_seconds=60)


@lru_cache(maxsize=1)
def _dummy_hash() -> str:
    return hash_password("qhi-auto-nonexistent-user-dummy")


def _rate_key(request: Request, action: str) -> str:
    host = request.client.host if request.client else "unknown"
    return f"{action}:{host}"


def _auth_response(customer: Customer, db: Session) -> AuthResponse:
    token, expires_at = issue_session(customer, db)
    db.commit()
    db.refresh(customer)
    return AuthResponse(access_token=token, expires_at=expires_at, customer=CustomerOut.model_validate(customer))


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> AuthResponse:
    register_limiter.check(_rate_key(request, "register"))
    customer = Customer(
        email_normalized=data.email,
        password_hash=hash_password(data.password.get_secret_value()),
        full_name=data.full_name,
        phone=data.phone,
        preferred_locale=data.preferred_locale,
        role="customer",
        is_active=True,
        email_verified=False,
    )
    db.add(customer)
    try:
        db.flush()
        response = _auth_response(customer, db)
        return response
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists") from error


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)) -> AuthResponse:
    login_limiter.check(_rate_key(request, "login"))
    email = data.email.strip().lower()
    customer = db.scalar(select(Customer).where(Customer.email_normalized == email))
    encoded = customer.password_hash if customer else _dummy_hash()
    valid_password = verify_password(data.password.get_secret_value(), encoded)
    if customer is None or not valid_password or not customer.is_active:
        raise HTTPException(status_code=401, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
    return _auth_response(customer, db)


@router.get("/me", response_model=CustomerOut)
def get_me(context: AuthContext = Depends(get_auth_context)) -> CustomerOut:
    return CustomerOut.model_validate(context.customer)


@router.patch("/me", response_model=CustomerOut)
def update_me(data: ProfileUpdate, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> CustomerOut:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(context.customer, key, value)
    db.commit()
    db.refresh(context.customer)
    return CustomerOut.model_validate(context.customer)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> None:
    context.session.revoked_at = datetime.now(UTC)
    db.commit()


@router.get("/me/sessions", response_model=list[CustomerSessionOut])
def list_my_sessions(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> list[CustomerSessionOut]:
    sessions = db.scalars(
        select(CustomerSession)
        .where(
            CustomerSession.customer_id == context.customer.id,
            CustomerSession.revoked_at.is_(None),
            CustomerSession.expires_at > datetime.now(UTC),
        )
        .order_by(CustomerSession.created_at.desc())
    ).all()
    return [
        CustomerSessionOut(
            id=session.id,
            created_at=session.created_at,
            expires_at=session.expires_at,
            current=session.id == context.session.id,
        )
        for session in sessions
    ]


@router.delete("/me/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_my_session(session_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> None:
    if session_id == context.session.id:
        raise HTTPException(status_code=409, detail="Use sign out to revoke the current session")
    session = db.scalar(
        select(CustomerSession).where(
            CustomerSession.id == session_id,
            CustomerSession.customer_id == context.customer.id,
            CustomerSession.revoked_at.is_(None),
        )
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    session.revoked_at = datetime.now(UTC)
    db.commit()


@router.get("/me/quotes", response_model=list[QuoteOut])
def my_quotes(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> list[QuoteOut]:
    quotes = db.scalars(select(PriceQuote).where(PriceQuote.customer_id == context.customer.id).order_by(PriceQuote.created_at.desc()).limit(100)).all()
    return [QuoteOut.model_validate(quote) for quote in quotes]


def _localized_car(car: Car, locale: str) -> CarOut:
    values = {key: getattr(car, key) for key in CarOut.model_fields if key not in {"images", "localized_title", "localized_description"}}
    values["images"] = [image.url for image in car.images]
    values["localized_title"] = next((item.title for item in car.translations if item.locale == locale), f"{car.brand} {car.model}")
    values["localized_description"] = next((item.description for item in car.translations if item.locale == locale), None)
    return CarOut.model_validate(values)


@router.get("/me/favorites", response_model=list[CarOut])
def get_favorites(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> list[CarOut]:
    cars = db.scalars(
        select(Car)
        .join(CustomerFavorite, CustomerFavorite.car_id == Car.id)
        .options(selectinload(Car.images), selectinload(Car.translations))
        .where(CustomerFavorite.customer_id == context.customer.id)
        .order_by(CustomerFavorite.created_at.desc())
    ).all()
    return [_localized_car(car, context.customer.preferred_locale) for car in cars]


@router.put("/me/favorites/{car_id}", response_model=FavoriteStatus)
def add_favorite(car_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> FavoriteStatus:
    car = db.scalar(select(Car).where(Car.id == car_id, Car.published.is_(True)))
    if car is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    existing = db.scalar(select(CustomerFavorite).where(CustomerFavorite.customer_id == context.customer.id, CustomerFavorite.car_id == car_id))
    if existing is None:
        db.add(CustomerFavorite(customer_id=context.customer.id, car_id=car_id))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            existing = db.scalar(select(CustomerFavorite).where(CustomerFavorite.customer_id == context.customer.id, CustomerFavorite.car_id == car_id))
            if existing is None:
                raise
    return FavoriteStatus(car_id=car_id, saved=True)


@router.delete("/me/favorites/{car_id}", response_model=FavoriteStatus)
def remove_favorite(car_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> FavoriteStatus:
    favorite = db.scalar(select(CustomerFavorite).where(CustomerFavorite.customer_id == context.customer.id, CustomerFavorite.car_id == car_id))
    if favorite is not None:
        db.delete(favorite)
        db.commit()
    return FavoriteStatus(car_id=car_id, saved=False)


@router.get("/me/comparison", response_model=list[CarOut])
def get_comparison(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> list[CarOut]:
    rows = db.scalars(
        select(CustomerComparisonItem)
        .where(CustomerComparisonItem.customer_id == context.customer.id)
        .order_by(CustomerComparisonItem.position)
    ).all()
    car_ids = [row.car_id for row in rows]
    if not car_ids:
        return []
    cars = db.scalars(select(Car).options(selectinload(Car.images), selectinload(Car.translations)).where(Car.id.in_(car_ids))).all()
    by_id = {car.id: car for car in cars}
    return [_localized_car(by_id[car_id], context.customer.preferred_locale) for car_id in car_ids if car_id in by_id]


@router.put("/me/comparison", response_model=list[CarOut])
def set_comparison(data: ComparisonUpdate, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> list[CarOut]:
    if data.car_ids:
        found = set(db.scalars(select(Car.id).where(Car.id.in_(data.car_ids), Car.published.is_(True))).all())
        if found != set(data.car_ids):
            raise HTTPException(status_code=404, detail="One or more vehicles are unavailable")
    db.execute(delete(CustomerComparisonItem).where(CustomerComparisonItem.customer_id == context.customer.id))
    db.flush()
    db.add_all(CustomerComparisonItem(customer_id=context.customer.id, car_id=car_id, position=position) for position, car_id in enumerate(data.car_ids))
    db.commit()
    if not data.car_ids:
        return []
    cars = db.scalars(select(Car).options(selectinload(Car.images), selectinload(Car.translations)).where(Car.id.in_(data.car_ids))).all()
    by_id = {car.id: car for car in cars}
    return [_localized_car(by_id[car_id], context.customer.preferred_locale) for car_id in data.car_ids]



def _order_query():
    return select(VehicleOrder).options(selectinload(VehicleOrder.car), selectinload(VehicleOrder.events))


def _staff_order_query():
    return _order_query().options(selectinload(VehicleOrder.customer))


@router.post("/me/orders", response_model=OrderOut, status_code=201)
def create_order(data: OrderCreate, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> OrderOut:
    car = db.scalar(select(Car).where(Car.id == data.car_id, Car.published.is_(True)))
    if car is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    order = VehicleOrder(
        order_number=f"QHI-{datetime.now(UTC).year}-{secrets.token_hex(4).upper()}",
        customer_id=context.customer.id,
        car_id=car.id,
        status="requested",
        customer_note=data.customer_note,
    )
    db.add(order)
    db.flush()
    db.add(OrderEvent(order_id=order.id, actor_id=context.customer.id, event_type="created", status="requested"))
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="Could not create order; retry the request") from error
    result = db.scalar(_order_query().where(VehicleOrder.id == order.id))
    return OrderOut.model_validate(result)


@router.get("/me/orders", response_model=list[OrderOut])
def list_my_orders(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> list[OrderOut]:
    orders = db.scalars(_order_query().where(VehicleOrder.customer_id == context.customer.id).order_by(VehicleOrder.created_at.desc())).all()
    return [OrderOut.model_validate(order) for order in orders]


@router.get("/me/orders/{order_id}", response_model=OrderOut)
def get_my_order(order_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> OrderOut:
    order = db.scalar(_order_query().where(VehicleOrder.id == order_id, VehicleOrder.customer_id == context.customer.id))
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderOut.model_validate(order)


@router.post("/me/orders/{order_id}/cancel", response_model=OrderOut)
def cancel_my_order(order_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> OrderOut:
    order = db.scalar(_order_query().where(VehicleOrder.id == order_id, VehicleOrder.customer_id == context.customer.id).with_for_update())
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    try:
        order.status = transition_order(order.status, "cancelled")
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    db.add(OrderEvent(order_id=order.id, actor_id=context.customer.id, event_type="status_changed", status="cancelled", public_note="Cancellation requested by customer"))
    db.commit()
    db.refresh(order)
    return OrderOut.model_validate(db.scalar(_order_query().where(VehicleOrder.id == order.id)))


@router.get("/staff/orders", response_model=list[StaffOrderOut])
def staff_list_orders(context: AuthContext = Depends(require_staff), db: Session = Depends(get_db)) -> list[StaffOrderOut]:
    orders = db.scalars(_staff_order_query().order_by(VehicleOrder.created_at.desc()).limit(200)).all()
    return [StaffOrderOut.model_validate(order) for order in orders]


@router.patch("/staff/orders/{order_id}/status", response_model=StaffOrderOut)
def staff_update_order(order_id: int, data: OrderStatusChange, context: AuthContext = Depends(require_staff), db: Session = Depends(get_db)) -> StaffOrderOut:
    order = db.scalar(_staff_order_query().where(VehicleOrder.id == order_id).with_for_update())
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    try:
        order.status = transition_order(order.status, data.status)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    db.add(OrderEvent(order_id=order.id, actor_id=context.customer.id, event_type="status_changed", status=data.status, public_note=data.public_note, internal_note=data.internal_note))
    db.commit()
    return StaffOrderOut.model_validate(db.scalar(_staff_order_query().where(VehicleOrder.id == order.id)))
