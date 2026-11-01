from collections import OrderedDict, deque
from datetime import UTC, datetime
from hashlib import sha256
from math import floor
from threading import Lock
from time import monotonic

from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.rate_limit import RateLimitBucket


class SlidingWindowLimiter:
    """Process-local abuse guard. Production must also enforce limits at the edge."""

    def __init__(self, max_requests: int, window_seconds: int, max_keys: int = 4096) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._hits: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = Lock()
        self._database_checks = 0

    def check(self, key: str, db: Session | None = None) -> None:
        if db is not None:
            try:
                if db.get_bind().dialect.name == "postgresql":
                    self._check_postgres(key, db)
                    return
            except (AttributeError, TypeError):
                pass
        self._check_local(key)

    def _check_postgres(self, key: str, db: Session) -> None:
        now = datetime.now(UTC)
        epoch = floor(now.timestamp() / self.window_seconds) * self.window_seconds
        window_start = datetime.fromtimestamp(epoch, UTC)
        statement = insert(RateLimitBucket).values(
            key_digest=sha256(key.encode("utf-8")).hexdigest(),
            window_start=window_start,
            request_count=1,
        )
        statement = statement.on_conflict_do_update(
            constraint="uq_rate_limit_key_window",
            set_={"request_count": RateLimitBucket.request_count + 1},
            where=RateLimitBucket.request_count < self.max_requests,
        ).returning(RateLimitBucket.request_count)
        try:
            count = db.scalar(statement)
            if count is None:
                db.rollback()
                raise HTTPException(status_code=429, detail="Too many requests")
            with self._lock:
                self._database_checks += 1
                cleanup = self._database_checks % 100 == 0
            if cleanup:
                cutoff = datetime.fromtimestamp(now.timestamp() - self.window_seconds * 2, UTC)
                db.execute(delete(RateLimitBucket).where(RateLimitBucket.window_start < cutoff))
            db.commit()
        except HTTPException:
            raise
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=503, detail="Rate limiting is temporarily unavailable") from None

    def _check_local(self, key: str) -> None:
        now = monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            hits = self._hits.pop(key, deque())
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.max_requests:
                self._hits[key] = hits
                raise HTTPException(status_code=429, detail="Too many requests")
            hits.append(now)
            self._hits[key] = hits
            while len(self._hits) > self.max_keys:
                self._hits.popitem(last=False)
