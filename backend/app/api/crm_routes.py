from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, get_optional_customer, require_staff
from app.core.rate_limit import SlidingWindowLimiter
from app.db.session import get_db
from app.models import CRMInteraction, CRMLead, Customer, PriceQuote, VehicleOrder
from app.schemas.crm import CRMAnalytics, CRMManagerWorkload, CRMOverview, InteractionCreate, InteractionOut, LeadCreate, LeadOut, LeadReceipt, LeadStatus, LeadUpdate, ManagerOut
from app.services.crm import transition_lead

router = APIRouter(tags=["crm"])
lead_limiter = SlidingWindowLimiter(max_requests=4, window_seconds=60)
@router.post("/leads", response_model=LeadReceipt, status_code=status.HTTP_201_CREATED)
def submit_lead(
    data: LeadCreate,
    request: Request,
    customer: Customer | None = Depends(get_optional_customer),
    db: Session = Depends(get_db),
) -> LeadReceipt:
    host = request.client.host if request.client else "unknown"
    lead_limiter.check(f"lead:{host}")
    lead = CRMLead(
        customer_id=customer.id if customer else None,
        name=customer.full_name if customer else data.name,
        email=customer.email_normalized if customer else data.email,
        phone=customer.phone if customer else data.phone,
        preferred_locale=customer.preferred_locale if customer else data.preferred_locale,
        source="website",
        status="new",
        message=data.message,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return LeadReceipt(id=lead.id)


@router.get("/crm/leads", response_model=list[LeadOut])
def list_leads(
    status_filter: LeadStatus | None = Query(default=None, alias="status"),
    manager_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: AuthContext = Depends(require_staff),
    db: Session = Depends(get_db),
) -> list[LeadOut]:
    statement = select(CRMLead)
    if status_filter:
        statement = statement.where(CRMLead.status == status_filter)
    if manager_id:
        statement = statement.where(CRMLead.assigned_manager_id == manager_id)
    leads = db.scalars(statement.order_by(CRMLead.created_at.desc()).limit(limit).offset(offset)).all()
    return [LeadOut.model_validate(lead) for lead in leads]


@router.get("/crm/managers", response_model=list[ManagerOut])
def list_managers(context: AuthContext = Depends(require_staff), db: Session = Depends(get_db)) -> list[ManagerOut]:
    managers = db.scalars(
        select(Customer)
        .where(Customer.is_active.is_(True), Customer.role.in_(("manager", "admin")))
        .order_by(Customer.full_name, Customer.id)
    ).all()
    return [ManagerOut.model_validate(manager) for manager in managers]


@router.patch("/crm/leads/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, data: LeadUpdate, context: AuthContext = Depends(require_staff), db: Session = Depends(get_db)) -> LeadOut:
    lead = db.scalar(select(CRMLead).where(CRMLead.id == lead_id).with_for_update())
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    changes = data.model_dump(exclude_unset=True)
    if "assigned_manager_id" in changes and changes["assigned_manager_id"] is not None:
        manager = db.scalar(select(Customer).where(Customer.id == changes["assigned_manager_id"], Customer.is_active.is_(True)))
        if manager is None or manager.role not in {"manager", "admin"}:
            raise HTTPException(status_code=422, detail="Assigned user is not an active manager")
    new_status = changes.get("status")
    if new_status is not None and new_status != lead.status:
        try:
            lead.status = transition_lead(lead.status, new_status)
        except ValueError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        db.add(CRMInteraction(lead_id=lead.id, actor_id=context.customer.id, kind="note", summary=f"Lead status changed to {new_status}"))
    if "assigned_manager_id" in changes:
        lead.assigned_manager_id = changes["assigned_manager_id"]
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.post("/crm/leads/{lead_id}/interactions", response_model=InteractionOut, status_code=status.HTTP_201_CREATED)
def add_interaction(lead_id: int, data: InteractionCreate, context: AuthContext = Depends(require_staff), db: Session = Depends(get_db)) -> InteractionOut:
    if db.get(CRMLead, lead_id) is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    interaction = CRMInteraction(lead_id=lead_id, actor_id=context.customer.id, kind=data.kind, summary=data.summary)
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return InteractionOut.model_validate(interaction)


@router.get("/crm/leads/{lead_id}/interactions", response_model=list[InteractionOut])
def list_interactions(lead_id: int, context: AuthContext = Depends(require_staff), db: Session = Depends(get_db)) -> list[InteractionOut]:
    if db.get(CRMLead, lead_id) is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    rows = db.scalars(select(CRMInteraction).where(CRMInteraction.lead_id == lead_id).order_by(CRMInteraction.created_at)).all()
    return [InteractionOut.model_validate(row) for row in rows]


@router.get("/crm/overview", response_model=CRMOverview)
def crm_overview(context: AuthContext = Depends(require_staff), db: Session = Depends(get_db)) -> CRMOverview:
    leads = db.execute(select(CRMLead.status, func.count(CRMLead.id)).group_by(CRMLead.status)).all()
    orders = db.execute(select(VehicleOrder.status, func.count(VehicleOrder.id)).group_by(VehicleOrder.status)).all()
    return CRMOverview(leads_by_status={key: count for key, count in leads}, orders_by_status={key: count for key, count in orders})


@router.get("/crm/analytics", response_model=CRMAnalytics)
def crm_analytics(
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    context: AuthContext = Depends(require_staff),
    db: Session = Depends(get_db),
) -> CRMAnalytics:
    today = datetime.now(UTC).date()
    period_end = to_date or today
    if to_date is not None and to_date > today:
        raise HTTPException(status_code=422, detail="to_date cannot be in the future")
    if from_date is None and period_end < date.min + timedelta(days=29):
        raise HTTPException(status_code=422, detail="Date is too early for the default analytics period")
    period_start = from_date or period_end - timedelta(days=29)
    if period_start > period_end:
        raise HTTPException(status_code=422, detail="from_date must not be later than to_date")
    if (period_end - period_start).days > 365:
        raise HTTPException(status_code=422, detail="Analytics period cannot exceed 366 calendar days")
    period_start_at = datetime.combine(period_start, time.min, tzinfo=UTC)
    period_end_at = datetime.combine(period_end + timedelta(days=1), time.min, tzinfo=UTC)
    lead_period = (CRMLead.created_at >= period_start_at, CRMLead.created_at < period_end_at)
    order_period = (VehicleOrder.created_at >= period_start_at, VehicleOrder.created_at < period_end_at)
    quote_period = (PriceQuote.created_at >= period_start_at, PriceQuote.created_at < period_end_at)

    lead_status_rows = db.execute(select(CRMLead.status, func.count(CRMLead.id)).where(*lead_period).group_by(CRMLead.status)).all()
    lead_source_rows = db.execute(select(CRMLead.source, func.count(CRMLead.id)).where(*lead_period).group_by(CRMLead.source)).all()
    leads_by_status = {key: count for key, count in lead_status_rows}
    leads_created = sum(leads_by_status.values())
    converted_leads = leads_by_status.get("converted", 0)
    conversion_rate = (Decimal(converted_leads * 100) / Decimal(leads_created)).quantize(Decimal("0.01")) if leads_created else Decimal("0.00")

    manager_rows = db.execute(
        select(
            Customer.id,
            Customer.full_name,
            func.count(CRMLead.id),
            func.coalesce(func.sum(case((CRMLead.status.notin_(("converted", "lost")), 1), else_=0)), 0),
        )
        .join(CRMLead, CRMLead.assigned_manager_id == Customer.id)
        .where(Customer.is_active.is_(True), Customer.role.in_(("manager", "admin")), *lead_period)
        .group_by(Customer.id, Customer.full_name)
        .order_by(Customer.full_name, Customer.id)
    ).all()
    manager_workload = [
        CRMManagerWorkload(manager_id=manager_id, manager_name=name, assigned_leads=assigned, active_leads=active)
        for manager_id, name, assigned, active in manager_rows
    ]
    assigned_to_active_staff = sum(item.assigned_leads for item in manager_workload)

    order_status_rows = db.execute(select(VehicleOrder.status, func.count(VehicleOrder.id)).where(*order_period).group_by(VehicleOrder.status)).all()
    orders_by_status = {key: count for key, count in order_status_rows}
    orders_created = sum(orders_by_status.values())
    quote_count, quoted_total = db.execute(
        select(func.count(PriceQuote.id), func.coalesce(func.sum(PriceQuote.total_tjs), 0)).where(*quote_period)
    ).one()

    return CRMAnalytics(
        from_date=period_start,
        to_date=period_end,
        leads_created=leads_created,
        leads_by_status=leads_by_status,
        leads_by_source={key: count for key, count in lead_source_rows},
        converted_leads=converted_leads,
        conversion_rate_percent=conversion_rate,
        unassigned_leads=max(0, leads_created - assigned_to_active_staff),
        manager_workload=manager_workload,
        orders_created=orders_created,
        orders_by_status=orders_by_status,
        quotes_created=quote_count,
        quoted_total_tjs=quoted_total,
    )
