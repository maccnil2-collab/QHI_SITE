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


def test_comparison_is_limited_to_three_unique_vehicles():
    from pydantic import ValidationError
    from app.schemas.customer import ComparisonUpdate

    assert ComparisonUpdate(car_ids=[1, 2, 3]).car_ids == [1, 2, 3]
    with pytest.raises(ValidationError):
        ComparisonUpdate(car_ids=[1, 2, 3, 4])
    with pytest.raises(ValidationError):
        ComparisonUpdate(car_ids=[1, 1])
