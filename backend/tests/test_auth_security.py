import pytest
from pydantic import ValidationError

from app.core.passwords import hash_password, verify_password
from app.core.rate_limit import SlidingWindowLimiter
from app.schemas.auth import RegisterRequest


def test_password_hash_is_salted_and_verifies_without_plaintext_storage():
    password = "CorrectHorseBatteryStaple!42"
    first = hash_password(password)
    second = hash_password(password)
    assert first.startswith("scrypt$32768$8$1$")
    assert first != second
    assert verify_password(password, first)
    assert not verify_password("incorrect password", first)
    assert not verify_password(password, "malformed")


def test_registration_normalizes_email_and_keeps_locale_selection():
    data = RegisterRequest(email=" Person@Example.com ", password="A-valid-long-passphrase-44", full_name="  Sample Person ", preferred_locale="tg")
    assert data.email == "person@example.com"
    assert data.full_name == "Sample Person"
    assert data.preferred_locale == "tg"
    with pytest.raises(ValidationError):
        RegisterRequest(email="not-an-email", password="A-valid-long-passphrase-44", full_name="Person")
    with pytest.raises(ValidationError):
        RegisterRequest(email="person@example.com", password="short", full_name="Person")


def test_auth_rate_limit_enforces_window_and_separates_clients():
    limiter = SlidingWindowLimiter(max_requests=2, window_seconds=30)
    limiter.check("login:client-a")
    limiter.check("login:client-a")
    limiter.check("login:client-b")
    with pytest.raises(Exception) as error:
        limiter.check("login:client-a")
    assert getattr(error.value, "status_code", None) == 429


def test_private_profile_requires_a_bearer_token_without_opening_database():
    from fastapi.testclient import TestClient
    from app.main import app

    response = TestClient(app).get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_session_management_contract_hides_token_material_and_protects_current_session():
    from datetime import UTC, datetime
    from types import SimpleNamespace
    from fastapi import HTTPException

    from app.api.auth_routes import revoke_my_session
    from app.schemas.auth import CustomerSessionOut

    created = datetime.now(UTC)
    session = CustomerSessionOut(id=12, created_at=created, expires_at=created, current=True)
    assert set(session.model_dump()) == {"id", "created_at", "expires_at", "current"}
    assert "token" not in session.model_dump()
    context = SimpleNamespace(session=SimpleNamespace(id=12), customer=SimpleNamespace(id=4))
    with pytest.raises(HTTPException) as error:
        revoke_my_session(12, context=context, db=None)
    assert error.value.status_code == 409


def test_session_revocation_cannot_target_another_customers_session():
    from types import SimpleNamespace
    from fastapi import HTTPException

    from app.api.auth_routes import revoke_my_session

    context = SimpleNamespace(session=SimpleNamespace(id=12), customer=SimpleNamespace(id=4))
    db = SimpleNamespace(scalar=lambda _query: None)
    with pytest.raises(HTTPException) as error:
        revoke_my_session(99, context=context, db=db)
    assert error.value.status_code == 404


def test_production_session_cookies_are_secure_and_removable(monkeypatch):
    from datetime import UTC, datetime, timedelta
    from fastapi import Response

    from app.core.auth import clear_session_cookies, set_session_cookies

    monkeypatch.setenv("APP_ENV", "production")
    response = Response()
    set_session_cookies(response, "opaque-session-value", datetime.now(UTC) + timedelta(days=1))
    cookie_headers = [value.decode("latin-1") for key, value in response.raw_headers if key.lower() == b"set-cookie"]
    session_cookie = next(value for value in cookie_headers if value.startswith("qhi_session="))
    csrf_cookie = next(value for value in cookie_headers if value.startswith("qhi_csrf="))
    assert "secure" in session_cookie.lower() and "httponly" in session_cookie.lower()
    assert "secure" in csrf_cookie.lower() and "httponly" not in csrf_cookie.lower()

    clear_session_cookies(response)
    cleared = [value.decode("latin-1") for key, value in response.raw_headers if key.lower() == b"set-cookie" and b"max-age=0" in value.lower()]
    assert len(cleared) == 2


def test_comparison_is_limited_to_three_unique_vehicles():
    from pydantic import ValidationError
    from app.schemas.customer import ComparisonUpdate

    assert ComparisonUpdate(car_ids=[1, 2, 3]).car_ids == [1, 2, 3]
    with pytest.raises(ValidationError):
        ComparisonUpdate(car_ids=[1, 2, 3, 4])
    with pytest.raises(ValidationError):
        ComparisonUpdate(car_ids=[1, 1])


@pytest.fixture
def cookie_auth_client(monkeypatch):
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.api import auth_routes
    from app.core.config import Settings
    from app.db import base, session as db_session
    from app.main import app

    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    base.Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(db_session, "SessionLocal", session_factory)
    monkeypatch.setattr(auth_routes, "settings", Settings(database_url="sqlite+pysqlite://", cors_origins=["http://localhost:3000"], admin_api_key=None))
    monkeypatch.delenv("APP_ENV", raising=False)
    with TestClient(app) as client:
        yield client
    engine.dispose()


def test_browser_auth_uses_http_only_cookie_and_csrf_protection(cookie_auth_client):
    client = cookie_auth_client
    payload = {
        "email": "cookie-user@example.test",
        "password": "A-valid-long-passphrase-44",
        "full_name": "Cookie User",
        "preferred_locale": "en",
    }
    origin = {"Origin": "http://localhost:3000"}

    rejected = client.post("/api/v1/auth/register", json=payload, headers={"Origin": "https://evil.example"})
    assert rejected.status_code == 403

    registered = client.post("/api/v1/auth/register", json=payload, headers=origin)
    assert registered.status_code == 201
    assert "access_token" not in registered.json()
    session_cookie = next(value for value in registered.headers.get_list("set-cookie") if value.startswith("qhi_session="))
    csrf_cookie = next(value for value in registered.headers.get_list("set-cookie") if value.startswith("qhi_csrf="))
    assert "httponly" in session_cookie.lower()
    assert "samesite=lax" in session_cookie.lower()
    assert "httponly" not in csrf_cookie.lower()

    restored = client.get("/api/v1/auth/me")
    assert restored.json()["email_normalized"] == payload["email"]
    assert restored.headers["x-csrf-token"] == registered.json()["csrf_token"]
    assert client.patch("/api/v1/auth/me", json={"full_name": "Updated Name"}).status_code == 403

    csrf = client.cookies.get("qhi_csrf")
    updated = client.patch("/api/v1/auth/me", json={"full_name": "Updated Name"}, headers={**origin, "X-CSRF-Token": csrf})
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Updated Name"

    logged_out = client.post("/api/v1/auth/logout", headers={**origin, "X-CSRF-Token": csrf})
    assert logged_out.status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401
