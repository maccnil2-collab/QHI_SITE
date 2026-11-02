from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class PaymentAttempt(Base):
    """Provider-neutral payment attempt record. No card data is stored here."""
    __tablename__ = "payment_attempts"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_payment_attempt_idempotency"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("vehicle_orders.id", ondelete="RESTRICT"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    provider: Mapped[str] = mapped_column(String(32), default="demo")
    provider_reference: Mapped[str | None] = mapped_column(String(180), nullable=True, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(64))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(32), default="not_started", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PaymentEvent(Base):
    """Append-only ledger events for simulated payments and refunds."""
    __tablename__ = "payment_events"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_payment_event_idempotency"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    payment_attempt_id: Mapped[int] = mapped_column(ForeignKey("payment_attempts.id", ondelete="RESTRICT"), index=True)
    actor_customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(32))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    idempotency_key: Mapped[str] = mapped_column(String(64))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
