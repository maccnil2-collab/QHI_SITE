"""Link priced quotes to orders and add an auditable payment event ledger.

Revision ID: 0013_order_payment_ledger
Revises: 0012_structured_vehicle_specs
"""
from alembic import op
import sqlalchemy as sa


revision = "0013_order_payment_ledger"
down_revision = "0012_structured_vehicle_specs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("price_quotes", sa.Column("car_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_price_quotes_car_id_cars", "price_quotes", "cars", ["car_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_price_quotes_car_id", "price_quotes", ["car_id"])

    op.add_column("vehicle_orders", sa.Column("quote_id", sa.Integer(), nullable=True))
    op.add_column("vehicle_orders", sa.Column("quoted_amount", sa.Numeric(14, 2), nullable=True))
    op.add_column("vehicle_orders", sa.Column("currency", sa.String(3), nullable=True))
    op.create_foreign_key("fk_vehicle_orders_quote_id_price_quotes", "vehicle_orders", "price_quotes", ["quote_id"], ["id"], ondelete="RESTRICT")
    op.create_index("ix_vehicle_orders_quote_id", "vehicle_orders", ["quote_id"])

    op.create_table(
        "payment_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payment_attempt_id", sa.Integer(), sa.ForeignKey("payment_attempts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("actor_customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("idempotency_key", sa.String(64), nullable=False),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_payment_event_idempotency"),
    )
    op.create_index("ix_payment_events_payment_attempt_id", "payment_events", ["payment_attempt_id"])
    op.create_index("ix_payment_events_actor_customer_id", "payment_events", ["actor_customer_id"])
    op.create_index("ix_payment_events_created_at", "payment_events", ["created_at"])


def downgrade() -> None:
    op.drop_table("payment_events")
    op.drop_index("ix_vehicle_orders_quote_id", table_name="vehicle_orders")
    op.drop_constraint("fk_vehicle_orders_quote_id_price_quotes", "vehicle_orders", type_="foreignkey")
    op.drop_column("vehicle_orders", "currency")
    op.drop_column("vehicle_orders", "quoted_amount")
    op.drop_column("vehicle_orders", "quote_id")
    op.drop_index("ix_price_quotes_car_id", table_name="price_quotes")
    op.drop_constraint("fk_price_quotes_car_id_cars", "price_quotes", type_="foreignkey")
    op.drop_column("price_quotes", "car_id")
