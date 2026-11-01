from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CRMLead(Base):
    __tablename__ = "crm_leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_manager_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(254), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    preferred_locale: Mapped[str] = mapped_column(String(2), default="ru")
    source: Mapped[str] = mapped_column(String(40), default="website")
    status: Mapped[str] = mapped_column(String(24), default="new", index=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    interactions: Mapped[list["CRMInteraction"]] = relationship(back_populates="lead", cascade="all, delete-orphan", order_by="CRMInteraction.created_at")
    customer: Mapped["Customer | None"] = relationship(foreign_keys=[customer_id])
    assigned_manager: Mapped["Customer | None"] = relationship(foreign_keys=[assigned_manager_id])


class CRMInteraction(Base):
    __tablename__ = "crm_interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("crm_leads.id", ondelete="CASCADE"), index=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(24))
    summary: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    lead: Mapped[CRMLead] = relationship(back_populates="interactions")
