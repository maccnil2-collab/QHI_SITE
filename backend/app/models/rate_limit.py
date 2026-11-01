from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RateLimitBucket(Base):
    __tablename__ = "rate_limit_buckets"
    __table_args__ = (
        UniqueConstraint("key_digest", "window_start", name="uq_rate_limit_key_window"),
        CheckConstraint("request_count > 0", name="ck_rate_limit_request_count_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    key_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False)
