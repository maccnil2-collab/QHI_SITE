from collections import OrderedDict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException


class SlidingWindowLimiter:
    """Process-local abuse guard. Production must also enforce limits at the edge."""

    def __init__(self, max_requests: int, window_seconds: int, max_keys: int = 4096) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._hits: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = Lock()

    def check(self, key: str) -> None:
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
