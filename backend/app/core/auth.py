from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import os
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import Cookie, Depends, Header, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Customer, CustomerSession

bearer_scheme = HTTPBearer(auto_error=False)
SESSION_COOKIE = "qhi_session"
CSRF_COOKIE = "qhi_csrf"
CSRF_HEADER = "X-CSRF-Token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
CSRF_MESSAGE = b"QHI AUTO session csrf v1"


@dataclass(frozen=True)
class AuthContext:
    customer: Customer
    session: CustomerSession
    raw_token: str = ""


def csrf_token_for_session(session_token: str) -> str:
    return hmac.new(session_token.encode("ascii"), CSRF_MESSAGE, hashlib.sha256).hexdigest()


def _request_token(
    *,
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
    session_cookie: str | None,
    csrf_cookie: str | None,
    csrf_header: str | None,
) -> str:
    if credentials is not None:
        if credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
        return credentials.credentials
    if session_cookie is None:
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    if request.method.upper() not in SAFE_METHODS:
        try:
            expected = csrf_token_for_session(session_cookie).encode("ascii")
            csrf_cookie_value = csrf_cookie.encode("ascii") if csrf_cookie is not None else b""
            csrf_header_value = csrf_header.encode("ascii") if csrf_header is not None else b""
        except UnicodeEncodeError as error:
            raise HTTPException(status_code=403, detail="CSRF validation failed") from error
        if (
            not hmac.compare_digest(csrf_cookie_value, expected)
            or not hmac.compare_digest(csrf_header_value, expected)
        ):
            raise HTTPException(status_code=403, detail="CSRF validation failed")
    return session_cookie


def _resolve_context(token: str, db: Session) -> AuthContext:
    try:
        digest = sha256(token.encode("ascii")).hexdigest()
    except UnicodeEncodeError as error:
        raise HTTPException(status_code=401, detail="Invalid bearer token", headers={"WWW-Authenticate": "Bearer"}) from error
    session = db.scalar(select(CustomerSession).options(joinedload(CustomerSession.customer)).where(CustomerSession.token_digest == digest))
    now = datetime.now(UTC)
    expires_at = session.expires_at if session is not None else now
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if session is None or session.revoked_at is not None or expires_at <= now or not session.customer.is_active:
        raise HTTPException(status_code=401, detail="Session is invalid or expired", headers={"WWW-Authenticate": "Bearer"})
    return AuthContext(customer=session.customer, session=session, raw_token=token)


def get_session_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session_cookie: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    csrf_cookie: str | None = Cookie(default=None, alias=CSRF_COOKIE),
    csrf_header: str | None = Header(default=None, alias=CSRF_HEADER),
) -> str:
    return _request_token(request=request, credentials=credentials, session_cookie=session_cookie, csrf_cookie=csrf_cookie, csrf_header=csrf_header)


def get_auth_context(
    token: str = Depends(get_session_token),
    db: Session = Depends(get_db),
) -> AuthContext:
    return _resolve_context(token, db)


def get_optional_customer(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session_cookie: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    csrf_cookie: str | None = Cookie(default=None, alias=CSRF_COOKIE),
    csrf_header: str | None = Header(default=None, alias=CSRF_HEADER),
    db: Session = Depends(get_db),
) -> Customer | None:
    if credentials is None and session_cookie is None:
        return None
    token = _request_token(request=request, credentials=credentials, session_cookie=session_cookie, csrf_cookie=csrf_cookie, csrf_header=csrf_header)
    return _resolve_context(token, db).customer


def get_current_customer(context: AuthContext = Depends(get_auth_context)) -> Customer:
    return context.customer


def issue_session(customer: Customer, db: Session) -> tuple[str, datetime]:
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=14)
    token = token_urlsafe(32)
    db.add(CustomerSession(customer_id=customer.id, token_digest=sha256(token.encode("ascii")).hexdigest(), expires_at=expires_at))
    return token, expires_at


def set_session_cookies(response: Response, token: str, expires_at: datetime) -> None:
    secure = os.getenv("APP_ENV", "development").lower() == "production"
    max_age = max(0, int((expires_at - datetime.now(UTC)).total_seconds()))
    common = {"path": "/", "secure": secure, "samesite": "lax", "max_age": max_age, "expires": expires_at}
    response.set_cookie(SESSION_COOKIE, token, httponly=True, **common)
    response.set_cookie(CSRF_COOKIE, csrf_token_for_session(token), httponly=False, **common)


def clear_session_cookies(response: Response) -> None:
    secure = os.getenv("APP_ENV", "development").lower() == "production"
    response.delete_cookie(SESSION_COOKIE, path="/", secure=secure, httponly=True, samesite="lax")
    response.delete_cookie(CSRF_COOKIE, path="/", secure=secure, httponly=False, samesite="lax")


def require_staff(context: AuthContext = Depends(get_auth_context)) -> AuthContext:
    if context.customer.role not in {"manager", "admin"}:
        raise HTTPException(status_code=403, detail="Staff access required")
    return context
