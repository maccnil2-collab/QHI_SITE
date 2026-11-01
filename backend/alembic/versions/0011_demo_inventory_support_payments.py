"""Add inventory metadata, support tickets, and provider-neutral payment attempts.

Revision ID: 0011_demo_inventory_support_payments
Revises: 0010_shared_rate_limit_buckets
"""
from alembic import op
import sqlalchemy as sa

revision = "0011_demo_inventory_support_payments"
down_revision = "0010_shared_rate_limit_buckets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for name, typ in (("category", sa.String(40)), ("engine_type", sa.String(40)), ("engine_cc", sa.Integer()), ("transmission", sa.String(40)), ("mileage_km", sa.Integer()), ("exterior_color", sa.String(80)), ("equipment", sa.Text()), ("specifications", sa.Text())):
        op.add_column("cars", sa.Column(name, typ, nullable=True))
    op.add_column("cars", sa.Column("fuel_consumption_l_100km", sa.Numeric(5, 2), nullable=True))
    op.add_column("cars", sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index("ix_cars_category", "cars", ["category"])
    op.create_index("ix_cars_is_demo", "cars", ["is_demo"])
    for name, typ in (("attribution", sa.String(500)), ("license_name", sa.String(120)), ("source_url", sa.Text())):
        op.add_column("car_images", sa.Column(name, typ, nullable=True))
    op.create_table(
        "support_tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_number", sa.String(24), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(160), nullable=False), sa.Column("email", sa.String(254), nullable=False),
        sa.Column("category", sa.String(32), nullable=False), sa.Column("subject", sa.String(180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False), sa.Column("locale", sa.String(2), nullable=False, server_default="en"),
        sa.Column("status", sa.String(24), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("ticket_number", name="uq_support_tickets_ticket_number"),
    )
    for col in ("ticket_number", "customer_id", "email", "category", "status", "created_at"):
        op.create_index(f"ix_support_tickets_{col}", "support_tickets", [col], unique=(col == "ticket_number"))
    op.create_table("support_ticket_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(24), nullable=False), sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_support_ticket_events_ticket_id", "support_ticket_events", ["ticket_id"])
    op.create_index("ix_support_ticket_events_actor_id", "support_ticket_events", ["actor_id"])
    op.create_table("payment_attempts",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("public_id", sa.String(36), nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("vehicle_orders.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False, server_default="demo"),
        sa.Column("provider_reference", sa.String(180)), sa.Column("idempotency_key", sa.String(64), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False), sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="not_started"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_payment_attempt_idempotency"),
        sa.UniqueConstraint("public_id", name="uq_payment_attempts_public_id"))
    for col in ("public_id", "order_id", "customer_id", "provider_reference", "status", "created_at"):
        op.create_index(f"ix_payment_attempts_{col}", "payment_attempts", [col], unique=(col == "public_id"))


def downgrade() -> None:
    op.drop_table("payment_attempts")
    op.drop_table("support_ticket_events")
    op.drop_table("support_tickets")
    for col in ("attribution", "license_name", "source_url"):
        op.drop_column("car_images", col)
    op.drop_index("ix_cars_is_demo", table_name="cars")
    op.drop_index("ix_cars_category", table_name="cars")
    for col in ("is_demo", "fuel_consumption_l_100km", "specifications", "equipment", "exterior_color", "mileage_km", "transmission", "engine_cc", "engine_type", "category"):
        op.drop_column("cars", col)
