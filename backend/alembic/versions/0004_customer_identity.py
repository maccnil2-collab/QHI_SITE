"""Customer identity, sessions, favorites, and quote ownership.

Revision ID: 0004_customer_identity
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_customer_identity"
down_revision = "0003_quote_snapshots"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email_normalized", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("phone", sa.String(32)),
        sa.Column("preferred_locale", sa.String(2), nullable=False, server_default="ru"),
        sa.Column("role", sa.String(24), nullable=False, server_default="customer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email_normalized", name="uq_customers_email_normalized"),
    )
    op.create_index("ix_customers_role", "customers", ["role"])
    op.create_table(
        "customer_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_digest", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_customer_sessions_customer_id", "customer_sessions", ["customer_id"])
    op.create_index("ix_customer_sessions_token_digest", "customer_sessions", ["token_digest"], unique=True)
    op.create_index("ix_customer_sessions_expires_at", "customer_sessions", ["expires_at"])
    op.create_table(
        "customer_favorites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("car_id", sa.Integer(), sa.ForeignKey("cars.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("customer_id", "car_id", name="uq_customer_favorite_car"),
    )
    op.create_index("ix_customer_favorites_customer_id", "customer_favorites", ["customer_id"])
    op.create_index("ix_customer_favorites_car_id", "customer_favorites", ["car_id"])
    op.create_table(
        "customer_comparison_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("car_id", sa.Integer(), sa.ForeignKey("cars.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("customer_id", "car_id", name="uq_customer_comparison_car"),
        sa.UniqueConstraint("customer_id", "position", name="uq_customer_comparison_position"),
    )
    op.create_index("ix_customer_comparison_items_customer_id", "customer_comparison_items", ["customer_id"])
    op.create_index("ix_customer_comparison_items_car_id", "customer_comparison_items", ["car_id"])
    op.add_column("price_quotes", sa.Column("customer_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_price_quotes_customer_id_customers", "price_quotes", "customers", ["customer_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_price_quotes_customer_id", "price_quotes", ["customer_id"])


def downgrade() -> None:
    op.drop_index("ix_price_quotes_customer_id", table_name="price_quotes")
    op.drop_constraint("fk_price_quotes_customer_id_customers", "price_quotes", type_="foreignkey")
    op.drop_column("price_quotes", "customer_id")
    op.drop_table("customer_comparison_items")
    op.drop_table("customer_favorites")
    op.drop_table("customer_sessions")
    op.drop_table("customers")
