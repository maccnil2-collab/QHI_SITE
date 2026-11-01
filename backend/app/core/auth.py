from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Customer, CustomerSession

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    customer: Customer
    session: CustomerSession


def require_bearer(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> HTTPAuthorizationCredentials:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    return credentials


def _resolve_context(credentials: HTTPAuthorizationCredentials, db: Session) -> AuthContext:
    try:
        digest = sha256(credentials.credentials.encode("ascii")).hexdigest()
    except UnicodeEncodeError as error:
        raise HTTPException(status_code=401, detail="Invalid bearer token", headers={"WWW-Authenticate": "Bearer"}) from error
    session = db.scalar(select(CustomerSession).options(joinedload(CustomerSession.customer)).where(CustomerSession.token_digest == digest))
    now = datetime.now(UTC)
    if session is None or session.revoked_at is not None or session.expires_at <= now or not session.customer.is_active:
        raise HTTPException(status_code=401, detail="Session is invalid or expired", headers={"WWW-Authenticate": "Bearer"})
    return AuthContext(customer=session.customer, session=session)


def get_auth_context(
    credentials: HTTPAuthorizationCredentials = Depends(require_bearer),
    db: Session = Depends(get_db),
) -> AuthContext:
    return _resolve_context(credentials, db)


def get_optional_customer(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Customer | None:
    if credentials is None:
        return None
    return _resolve_context(credentials, db).customer


def get_current_customer(context: AuthContext = Depends(get_auth_context)) -> Customer:
    return context.customer


def issue_session(customer: Customer, db: Session) -> tuple[str, datetime]:
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=14)
    token = token_urlsafe(32)
    db.add(CustomerSession(customer_id=customer.id, token_digest=sha256(token.encode("ascii")).hexdigest(), expires_at=expires_at))
    return token, expires_at


def require_staff(context: AuthContext = Depends(get_auth_context)) -> AuthContext:
    if context.customer.role not in {"manager", "admin"}:
        raise HTTPException(status_code=403, detail="Staff access required")
    return context
