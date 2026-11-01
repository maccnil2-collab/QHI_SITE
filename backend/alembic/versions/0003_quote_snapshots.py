"""Persist quote and tariff snapshots.

Revision ID: 0003_quote_snapshots
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_quote_snapshots"
down_revision = "0002_admin_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "price_quotes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tariff_id", sa.Integer(), sa.ForeignKey("pricing_tariffs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("tariff_name", sa.String(120), nullable=False),
        sa.Column("effective_on", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("price_cny", sa.Numeric(14, 2), nullable=False),
        sa.Column("cny_to_tjs", sa.Numeric(12, 6), nullable=False),
        sa.Column("shipping_tjs", sa.Numeric(14, 2), nullable=False),
        sa.Column("customs_rate", sa.Numeric(8, 6), nullable=False),
        sa.Column("customs_basis", sa.String(32), nullable=False),
        sa.Column("additional_tjs", sa.Numeric(14, 2), nullable=False),
        sa.Column("paperwork_tjs", sa.Numeric(14, 2), nullable=False),
        sa.Column("car_tjs", sa.Numeric(14, 2), nullable=False),
        sa.Column("customs_tjs", sa.Numeric(14, 2), nullable=False),
        sa.Column("total_tjs", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_price_quotes_tariff_id", "price_quotes", ["tariff_id"])


def downgrade() -> None:
    op.drop_table("price_quotes")
