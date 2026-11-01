from secrets import token_hex
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.auth import AuthContext, get_optional_customer, require_staff
from app.core.rate_limit import SlidingWindowLimiter
from app.db.session import get_db
from app.models import SupportTicket, SupportTicketEvent, Customer
from app.schemas.support import TicketCreate, TicketOut, TicketStatusUpdate

router = APIRouter(tags=["support"])
ticket_limiter = SlidingWindowLimiter(max_requests=4, window_seconds=3600)

@router.post("/support/tickets", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(data: TicketCreate, request: Request, customer: Customer | None = Depends(get_optional_customer), db: Session = Depends(get_db)) -> TicketOut:
    host = request.client.host if request.client else "unknown"
    ticket_limiter.check(f"support:{host}", db)
    ticket = SupportTicket(ticket_number=f"QHI-{token_hex(5).upper()}", customer_id=customer.id if customer else None,
        name=customer.full_name if customer else data.name, email=customer.email_normalized if customer else data.email,
        category=data.category, subject=data.subject, message=data.message, locale=data.locale, status="open")
    db.add(ticket)
    db.flush()
    db.add(SupportTicketEvent(ticket_id=ticket.id, status="open", note="Ticket received"))
    db.commit()
    db.refresh(ticket)
    return TicketOut.model_validate(ticket)

@router.get("/support/tickets", response_model=list[TicketOut])
def list_tickets(context: AuthContext = Depends(require_staff), db: Session = Depends(get_db), limit: int = 50, offset: int = 0) -> list[TicketOut]:
    if not 1 <= limit <= 100 or offset < 0:
        raise HTTPException(status_code=422, detail="Invalid pagination")
    rows = db.scalars(select(SupportTicket).order_by(SupportTicket.created_at.desc()).limit(limit).offset(offset)).all()
    return [TicketOut.model_validate(row) for row in rows]

@router.patch("/support/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, data: TicketStatusUpdate, context: AuthContext = Depends(require_staff), db: Session = Depends(get_db)) -> TicketOut:
    ticket = db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id).with_for_update())
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if data.status != ticket.status:
        ticket.status = data.status
        db.add(SupportTicketEvent(ticket_id=ticket.id, actor_id=context.customer.id, status=data.status, note=data.note))
    db.commit()
    db.refresh(ticket)
    return TicketOut.model_validate(ticket)
