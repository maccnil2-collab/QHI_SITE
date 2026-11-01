"""Initial catalog and configurable pricing schema.

Revision ID: 0001_catalog_pricing
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_catalog_pricing"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("cars",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("brand", sa.String(80), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("trim", sa.String(120)),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("price_cny", sa.Numeric(14, 2), nullable=False),
        sa.Column("range_km", sa.Integer()),
        sa.Column("battery_kwh", sa.Numeric(7, 2)),
        sa.Column("power_kw", sa.Integer()),
        sa.Column("drivetrain", sa.String(32)),
        sa.Column("availability", sa.String(24), nullable=False, server_default="on_request"),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cars_slug", "cars", ["slug"], unique=True)
    op.create_index("ix_cars_brand", "cars", ["brand"])
    op.create_index("ix_cars_model", "cars", ["model"])
    op.create_index("ix_cars_year", "cars", ["year"])
    op.create_index("ix_cars_published", "cars", ["published"])
    op.create_table("car_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("car_id", sa.Integer(), sa.ForeignKey("cars.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("alt", sa.String(240)),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_car_images_car_id", "car_images", ["car_id"])
    op.create_table("car_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("car_id", sa.Integer(), sa.ForeignKey("cars.id", ondelete="CASCADE"), nullable=False),
        sa.Column("locale", sa.String(2), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("description", sa.Text()),
        sa.UniqueConstraint("car_id", "locale", name="uq_car_translation_locale"),
    )
    op.create_index("ix_car_translations_car_id", "car_translations", ["car_id"])
    op.create_index("ix_car_translations_locale", "car_translations", ["locale"])
    op.create_table("pricing_tariffs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="TJS"),
        sa.Column("cny_to_tjs", sa.Numeric(12, 6)),
        sa.Column("shipping_tjs", sa.Numeric(14, 2)),
        sa.Column("customs_rate", sa.Numeric(8, 6)),
        sa.Column("customs_basis", sa.String(32)),
        sa.Column("additional_tjs", sa.Numeric(14, 2)),
        sa.Column("paperwork_tjs", sa.Numeric(14, 2)),
        sa.Column("effective_on", sa.Date(), nullable=False),
        sa.Column("source_note", sa.String(500)),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_pricing_tariffs_active", "pricing_tariffs", ["active"])


def downgrade() -> None:
    op.drop_table("pricing_tariffs")
    op.drop_table("car_translations")
    op.drop_table("car_images")
    op.drop_table("cars")
