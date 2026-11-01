import hmac
from typing import Annotated

from fastapi import Header, HTTPException

from app.core.config import settings


def require_admin(token: Annotated[str | None, Header(alias="X-Admin-Token")] = None) -> str:
    expected = settings.admin_api_key
    if not expected or len(expected) < 32 or expected == "REPLACE_WITH_RANDOM_SECRET":
        raise HTTPException(status_code=503, detail="Administrative access is not configured")
    if token is None or not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Invalid administrative credentials")
    return "admin-api-key"
